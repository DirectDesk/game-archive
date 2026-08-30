from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..downloader import DownloadWorker
from ..models import DownloadTask, Game
from ..schemas import DownloadCreate, DownloadOut

router = APIRouter(prefix="/api/downloads", tags=["downloads"])
worker: DownloadWorker | None = None


def set_worker(value: DownloadWorker):
    global worker
    worker = value


@router.get("", response_model=list[DownloadOut])
async def list_downloads(db: AsyncSession = Depends(get_db)):
    return list((await db.scalars(select(DownloadTask).order_by(desc(DownloadTask.created_at)))).all())


@router.post("", response_model=DownloadOut)
async def create_download(payload: DownloadCreate, db: AsyncSession = Depends(get_db)):
    game = await db.get(Game, payload.game_id)
    if not game:
        raise HTTPException(404, "游戏不存在")
    if not payload.target_path.startswith("/"):
        raise HTTPException(422, "目标路径必须是容器内绝对路径")
    task = DownloadTask(**payload.model_dump())
    db.add(task)
    game.play_status = "downloading"
    await db.commit()
    await db.refresh(task)
    await worker.enqueue(task.id)  # type: ignore[union-attr]
    return task
