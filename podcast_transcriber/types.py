from datetime import datetime as DateTime
from enum import Enum
from typing import List, NamedTuple

from pydantic import AnyUrl, BaseModel, validator
from whisper import Whisper


class EpisodeSlug(str):
    pass


class PodcastId(str):
    pass


class PodcastInfo(BaseModel):
    podcast_id: PodcastId
    podcast_url: AnyUrl
    premium: bool
    enabled: bool


class Enclosure(BaseModel):
    url: str
    file_size: int
    mime_type: str


class Episode(BaseModel):
    title: str
    enclosures: List[Enclosure]
    published: DateTime

    @validator("published", pre=True)
    def convert_published_to_date_time(cls, published: str | int) -> DateTime:
        if isinstance(published, int):
            return DateTime.fromtimestamp(published)
        else:
            return DateTime.strptime(published, r"%Y-%m-%dT%H:%M:%S")


class PodcastFeed(BaseModel):
    title: str
    episodes: List[Episode]


class ModelName(str, Enum):
    TINY_EN = "tiny.en"
    BASE_EN = "base.en"


class NamedModel(NamedTuple):
    name: ModelName
    model: Whisper


class Segment(BaseModel):
    id: int
    seek: int
    start: float
    end: float
    text: str
    tokens: List[int]
    temperature: float
    avg_logprob: float
    compression_ratio: float
    no_speech_prob: float


class Transcript(BaseModel):
    text: str
    segments: List[Segment]
    language: str
