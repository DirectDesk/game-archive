from datetime import date

import httpx

from ..config import settings


class RawgClient:
    base_url = "https://api.rawg.io/api"

    def __init__(self):
        if not settings.rawg_api_key:
            raise ValueError("未配置 RAWG_API_KEY")

    async def search_games(self, query: str, page_size: int = 10) -> list[dict]:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(
                f"{self.base_url}/games",
                params={"key": settings.rawg_api_key, "search": query, "page_size": page_size},
            )
            response.raise_for_status()
            return [
                {"source_type": "rawg", "source_id": str(item["id"]), "title": item.get("name", ""), "cover_url": item.get("background_image", "")}
                for item in response.json().get("results", [])
            ]

    async def get_game_detail(self, rawg_id: str) -> dict:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(
                f"{self.base_url}/games/{rawg_id}",
                params={"key": settings.rawg_api_key},
            )
            response.raise_for_status()
            return self._map_detail(response.json())

    @staticmethod
    def _map_detail(item: dict) -> dict:
        developers = ", ".join(value.get("name", "") for value in item.get("developers", []))
        publishers = ", ".join(value.get("name", "") for value in item.get("publishers", []))
        tags = ", ".join(value.get("name", "") for value in item.get("tags", []))
        release_date = item.get("released")
        return {
            "title": item.get("name", ""),
            "alias": "",
            "cover_url": item.get("background_image", ""),
            "description": item.get("description_raw", "") or "",
            "developer": developers,
            "publisher": publishers,
            "release_date": date.fromisoformat(release_date) if release_date else None,
            "rating": (item.get("rating") or 0) * 20 if item.get("rating") is not None else None,
            "tags": tags,
            "series": "",
            "source_type": "rawg",
            "source_id": str(item.get("id", "")),
        }
