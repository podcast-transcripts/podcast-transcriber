import json
from pathlib import Path
from typing import List

from podcast_transcriber.types import PodcastInfo


def get_podcast_infos(file_path: Path) -> List[PodcastInfo]:
    with open(file_path, "r") as f:
        return [PodcastInfo(**p) for p in json.load(f)]
