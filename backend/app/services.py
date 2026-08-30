import httpx


async def search_vndb(query: str) -> list[dict]:
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post("https://api.vndb.org/kana/vn", json={"filters": ["search", "=", query], "fields": "id,title,alttitle,description,image.url,developers.name,released,rating,tags.name", "results": 20})
        response.raise_for_status()
        results = []
        for item in response.json().get("results", []):
            results.append({"source_type": "vndb", "source_id": item.get("id", ""), "title": item.get("title", ""), "alias": item.get("alttitle", ""), "cover_url": (item.get("image") or {}).get("url", ""), "description": item.get("description", ""), "developer": ", ".join(x.get("name", "") for x in item.get("developers", [])), "publisher": "", "release_date": item.get("released"), "rating": item.get("rating"), "tags": ", ".join(x.get("name", "") for x in item.get("tags", [])), "series": ""})
        return results
