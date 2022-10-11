import json
from logging import getLogger as get_logger
from pathlib import Path
from typing import List

from podcast_transcriber.types import PodcastInfo

LOGGER = get_logger(__name__)


def get_podcast_infos(file_path: Path) -> List[PodcastInfo]:
    LOGGER.info(f"Reading podcast infos from `{file_path.resolve()}`.")
    with open(file_path, "r") as f:
        return [PodcastInfo(**p) for p in json.load(f)]
