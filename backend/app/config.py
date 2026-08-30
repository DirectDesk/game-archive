import os
from pathlib import Path


class Settings:
    data_dir = Path(os.getenv("DATA_DIR", "/app/data"))
    database_url = f"sqlite+aiosqlite:///{data_dir / 'games.db'}"
    rawg_api_key = os.getenv("RAWG_API_KEY", "")
    download_timeout = float(os.getenv("DOWNLOAD_TIMEOUT", "60"))


settings = Settings()
