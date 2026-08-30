from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class GameBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    alias: str = ""
    cover_url: str = ""
    description: str = ""
    developer: str = ""
    publisher: str = ""
    release_date: date | None = None
    rating: float | None = Field(default=None, ge=0, le=100)
    tags: str = ""
    series: str = ""
    source_type: str = "custom"
    source_id: str = ""
    resource_type: str = "none"
    resource_url: str = ""
    play_status: str = "favorite"


class GameCreate(GameBase):
    pass


class GameUpdate(GameBase):
    pass


class GameOut(GameBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime


class DownloadCreate(BaseModel):
    game_id: int
    download_url: str = Field(min_length=1)
    target_path: str = Field(min_length=1)


class DownloadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    game_id: int
    download_url: str
    target_path: str
    file_size: int
    downloaded: int
    status: str
    error_msg: str
    created_at: datetime
    finished_at: datetime | None


class MetadataResult(BaseModel):
    source_type: str
    source_id: str
    title: str
    alias: str = ""
    cover_url: str = ""
    description: str = ""
    developer: str = ""
    publisher: str = ""
    release_date: date | None = None
    rating: float | None = None
    tags: str = ""
    series: str = ""
