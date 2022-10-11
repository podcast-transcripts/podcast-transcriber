import re
from logging import getLogger as get_logger
from pathlib import Path
from time import sleep

import requests

from podcast_transcriber.types import Episode, EpisodeSlug
from podcast_transcriber.utils import slugify

LOGGER = get_logger(__name__)

GET_FILE_EXTENSION_PATTERN = re.compile(r"\.([^.]+?)(?:\?.+)?$")


def get_episode_url(episode: Episode) -> str:
    return episode.enclosures[0].url


def get_file_extension(url: str) -> str:
    result = re.search(GET_FILE_EXTENSION_PATTERN, url)
    if result is None:
        raise ValueError(f"Could not file file extension of url `{url}`.")
    return result.group(1)


def download_file(url: str, file_path: Path) -> Path:
    if file_path.exists():
        LOGGER.info(f"File `{file_path.resolve()}` already exists, skipping download.")
    else:
        LOGGER.info(f"Downloading url `{url}` to `{file_path.resolve()}`.")
        response = requests.get(url)
        response.raise_for_status()
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(response.content)
        sleep(1)
    return file_path


def get_episode_audio_file_path(
    podcast_id: str, episode: Episode, data_folder: Path
) -> Path:
    episode_url = get_episode_url(episode)
    file_extension = get_file_extension(episode_url)
    episode_slug = EpisodeSlug(slugify(episode.title))
    file_name = episode_slug + "." + file_extension
    return data_folder / "raw" / "audio" / podcast_id / file_name


def download_episode_audio(
    podcast_id: str, episode: Episode, data_folder: Path
) -> Path:
    episode_url = get_episode_url(episode)
    episode_audio_file_path = get_episode_audio_file_path(
        podcast_id, episode, data_folder
    )
    return download_file(episode_url, episode_audio_file_path)
