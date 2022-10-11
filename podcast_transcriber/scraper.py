import json
import urllib.request
from pathlib import Path
from typing import Any, Dict

import podcastparser

from podcast_transcriber.podcast_infos import PodcastInfo
from podcast_transcriber.types import PodcastFeed
from podcast_transcriber.utils import create_parent_folder


def get_podcast_feed_file_path(podcast_info: PodcastInfo, data_folder: Path):
    return data_folder / "raw" / "podcast-feeds" / (podcast_info.podcast_id + ".json")


def write_raw_podcast_feed(
    podcast_feed: PodcastFeed, podcast_feed_file_path: Path
) -> Path:
    create_parent_folder(podcast_feed_file_path)
    with open(podcast_feed_file_path, "w") as f:
        f.write(podcast_feed.json())
    return podcast_feed_file_path


def scrape_podcast_feed(podcast_info: PodcastInfo, data_folder: Path) -> PodcastFeed:
    print(
        f"Scraping podcast feed for podcast `{podcast_info.podcast_id}` from `{podcast_info.podcast_url}`."
    )
    with urllib.request.urlopen(podcast_info.podcast_url) as stream:
        podcast_feed_dict: Dict[str, Any] = podcastparser.parse(podcast_info.podcast_url, stream)  # type: ignore
    podcast_feed = PodcastFeed(**podcast_feed_dict)
    write_raw_podcast_feed(
        podcast_feed, get_podcast_feed_file_path(podcast_info, data_folder)
    )
    return podcast_feed


def read_podcast_feed_file(podcast_info: PodcastInfo, data_folder: Path) -> PodcastFeed:
    podcast_feed_file_path = get_podcast_feed_file_path(podcast_info, data_folder)
    with open(podcast_feed_file_path, "r") as f:
        return PodcastFeed(**json.load(f))
