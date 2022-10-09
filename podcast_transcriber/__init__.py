from pathlib import Path

import typer

from podcast_transcriber.audio_downloader import (
    EpisodeSlug,
    download_episode_audio,
    get_episode_audio_file_path,
)
from podcast_transcriber.collector import collect_data
from podcast_transcriber.podcast_infos import get_podcast_infos
from podcast_transcriber.podcast_scraper import (
    read_podcast_feed_file,
    scrape_podcast_feed,
)
from podcast_transcriber.transcriber import (
    ModelName,
    get_model,
    get_transcript_file_path,
    read_transcript_file,
    transcribe_episode,
)
from podcast_transcriber.utils import shuffled_dict, shuffled_list, slugify


def main(
    data_folder: Path = Path(".") / "data",
    model: ModelName = ModelName.BASE_EN,
    scrape: bool = True,
    download: bool = True,
    transcribe: bool = True,
    combine: bool = True,
    shuffle: bool = False,
):
    model_name: ModelName = model  # type: ignore

    # Read podcast infos file
    podcast_infos_file = data_folder / "podcast-infos.json"
    podcast_infos = get_podcast_infos(podcast_infos_file)
    if shuffle:
        podcast_infos = shuffled_list(podcast_infos)

    # Scrape feeds
    if scrape:
        podcast_feeds = {
            podcast_info.podcast_id: scrape_podcast_feed(podcast_info, data_folder)
            for podcast_info in podcast_infos
        }
    else:
        podcast_feeds = {
            podcast_info.podcast_id: read_podcast_feed_file(podcast_info, data_folder)
            for podcast_info in podcast_infos
        }
    if shuffle:
        podcast_feeds = shuffled_dict(podcast_feeds)

    # Extract podcast episodes
    podcast_episodes = {
        (podcast_id, EpisodeSlug(slugify(episode.title))): episode
        for podcast_id, podcast_feed in podcast_feeds.items()
        for episode in podcast_feed.episodes
    }
    if shuffle:
        podcast_episodes = shuffled_dict(podcast_episodes)

    # Download audio
    if download:
        podcast_audio_files = {
            (podcast_id, episode_slug): download_episode_audio(
                podcast_id, episode, data_folder
            )
            for (podcast_id, episode_slug), episode in podcast_episodes.items()
        }
    else:
        podcast_audio_files = {
            (podcast_id, episode_slug): get_episode_audio_file_path(
                podcast_id, episode, data_folder
            )
            for (podcast_id, episode_slug), episode in podcast_episodes.items()
        }
        podcast_audio_files = {
            k: v for k, v in podcast_audio_files.items() if v.exists()
        }
    if shuffle:
        podcast_audio_files = shuffled_dict(podcast_audio_files)

    # Transcribe
    if transcribe:
        the_model = get_model(model_name)
        transcripts = {
            (podcast_id, episode_slug, model_name): transcribe_episode(
                podcast_id, episode_slug, audio_file, the_model, data_folder
            )
            for (podcast_id, episode_slug), audio_file in podcast_audio_files.items()
        }
    else:
        transcript_file_paths = {
            (podcast_id, episode_slug, model_name): get_transcript_file_path(
                podcast_id, episode_slug, model_name, data_folder
            )
            for podcast_id, episode_slug in podcast_audio_files.keys()
            for model_name in ModelName
        }
        transcripts = {
            k: read_transcript_file(transcript_file_path)
            for k, transcript_file_path in transcript_file_paths.items()
            if transcript_file_path.exists()
        }
    if shuffle:
        transcripts = shuffled_dict(transcripts)

    # Collect
    if combine:
        _ = collect_data(
            podcast_infos,
            podcast_feeds,
            podcast_episodes,
            transcripts,
            data_folder,
        )


def run():
    typer.run(main)
