from datetime import datetime as DateTime
from pathlib import Path
from typing import Dict, List, Tuple

from pydantic import BaseModel

from podcast_transcriber.types import (
    Episode,
    EpisodeSlug,
    ModelName,
    PodcastFeed,
    PodcastId,
    PodcastInfo,
    Transcript,
)
from podcast_transcriber.utils import create_parent_folder, seconds_to_timestamp


class CollectedSegment(BaseModel):
    timestamp: str
    text: str


class CollectedTranscript(BaseModel):
    segments: List[CollectedSegment]


class CollectedEpisode(BaseModel):
    episode_title: str
    episode_slug: EpisodeSlug
    published: DateTime
    transcript: CollectedTranscript


class CollectedPodcast(BaseModel):
    podcast_id: str
    podcast_title: str
    episodes: List[CollectedEpisode]


class CollectedData(BaseModel):
    podcasts: List[CollectedPodcast]


def collect_data(
    podcast_infos: List[PodcastInfo],
    podcast_feeds: Dict[PodcastId, PodcastFeed],
    all_podcast_episodes: Dict[Tuple[PodcastId, EpisodeSlug], Episode],
    transcripts: Dict[Tuple[PodcastId, EpisodeSlug, ModelName], Transcript],
    data_folder: Path,
) -> Path:
    print("Collecting data into a single file.")
    collected_podcasts: List[CollectedPodcast] = []
    for podcast_info in podcast_infos:
        podcast_is_premium = podcast_info.premium
        if podcast_is_premium:
            continue

        podcast_id = podcast_info.podcast_id
        podcast_feed = podcast_feeds[podcast_id]
        podcast_title = podcast_feed.title
        podcast_episodes = {
            an_episode_slug: an_episode
            for (
                a_podcast_id,
                an_episode_slug,
            ), an_episode in all_podcast_episodes.items()
            if a_podcast_id == podcast_id
        }

        collected_episodes: List[CollectedEpisode] = []
        for episode_slug, episode in podcast_episodes.items():
            episode_title = episode.title
            episode_published = episode.published
            episode_transcripts = {
                a_model_name: a_transcript
                for (
                    a_podcast_id,
                    an_episode_slug,
                    a_model_name,
                ), a_transcript in transcripts.items()
                if a_podcast_id == podcast_id and an_episode_slug == episode_slug
            }
            best_episode_transcript = episode_transcripts.get(
                ModelName.BASE_EN, episode_transcripts.get(ModelName.TINY_EN, None)
            )
            if best_episode_transcript is None:
                # Skip episode if no transcript was found
                continue

            collected_segments: List[CollectedSegment] = []
            for segment in best_episode_transcript.segments:
                segment_timestamp = seconds_to_timestamp(segment.start)
                segment_text = segment.text.strip()
                collected_segment = CollectedSegment(
                    timestamp=segment_timestamp, text=segment_text
                )
                collected_segments.append(collected_segment)

            collected_transcript = CollectedTranscript(segments=collected_segments)

            collected_episode = CollectedEpisode(
                episode_title=episode_title,
                episode_slug=episode_slug,
                published=episode_published,
                transcript=collected_transcript,
            )
            collected_episodes.append(collected_episode)

        collected_podcast = CollectedPodcast(
            podcast_id=podcast_id,
            podcast_title=podcast_title,
            episodes=collected_episodes,
        )

        collected_podcasts.append(collected_podcast)

    collected_data = CollectedData(podcasts=collected_podcasts)

    output_file_path = data_folder / "cleaned" / "cleaned.json"
    print(f"Writing collected data to `{output_file_path.resolve()}`.")
    create_parent_folder(output_file_path)
    with open(output_file_path, "w") as f:
        f.write(collected_data.json())
    return output_file_path
