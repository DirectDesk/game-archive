import asyncio
from datetime import datetime
from pathlib import Path

import httpx
from sqlalchemy import select

from .config import settings
from .database import SessionLocal
from .models import DownloadTask, Game


class DownloadWorker:
    def __init__(self):
        self.queue: asyncio.Queue[int] = asyncio.Queue()
        self.task: asyncio.Task | None = None

    async def start(self):
        self.task = asyncio.create_task(self.run())

    async def stop(self):
        if self.task:
            self.task.cancel()
            await asyncio.gather(self.task, return_exceptions=True)

    async def enqueue(self, task_id: int):
        await self.queue.put(task_id)

    async def run(self):
        while True:
            task_id = await self.queue.get()
            try:
                await self.download(task_id)
            except Exception as exc:
                async with SessionLocal() as db:
                    item = await db.get(DownloadTask, task_id)
                    if item:
                        item.status, item.error_msg, item.finished_at = "failed", str(exc), datetime.utcnow()
                        await db.commit()
            finally:
                self.queue.task_done()

    async def download(self, task_id: int):
        async with SessionLocal() as db:
            item = await db.get(DownloadTask, task_id)
            if not item:
                return
            item.status = "running"
            await db.commit()
            url, target = item.download_url, Path(item.target_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        async with httpx.AsyncClient(timeout=settings.download_timeout, follow_redirects=True) as client:
            async with client.stream("GET", url) as response:
                response.raise_for_status()
                total = int(response.headers.get("content-length", 0))
                with target.open("wb") as output:
                    downloaded = 0
                    async for chunk in response.aiter_bytes(1024 * 1024):
                        output.write(chunk)
                        downloaded += len(chunk)
                        async with SessionLocal() as db:
                            current = await db.get(DownloadTask, task_id)
                            if current:
                                current.downloaded, current.file_size = downloaded, total
                                await db.commit()
        async with SessionLocal() as db:
            current = await db.get(DownloadTask, task_id)
            if current:
                current.status, current.finished_at, current.downloaded = "completed", datetime.utcnow(), downloaded
                game = await db.get(Game, current.game_id)
                if game:
                    game.resource_type, game.resource_url, game.play_status = "nas_path", str(target), "archived"
                await db.commit()
