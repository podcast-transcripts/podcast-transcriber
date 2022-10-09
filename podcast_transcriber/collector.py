from datetime import datetime as DateTime
from pathlib import Path
from typing import Dict, List, Tuple

from pydantic import BaseModel
from typing_extensions import Self

from podcast_transcriber.types import (
    Episode,
    EpisodeSlug,
    ModelName,
    PodcastFeed,
    PodcastId,
    PodcastInfo,
    Segment,
    Transcript,
)
from podcast_transcriber.utils import create_parent_folder, seconds_to_timestamp


class CollectedSegment(BaseModel):
    timestamp: str
    text: str

    @classmethod
    def from_raw_data(cls, segment: Segment) -> Self:
        return cls(
            timestamp=seconds_to_timestamp(segment.start),
            text=segment.text.strip(),
        )


class CollectedTranscript(BaseModel):
    segments: List[CollectedSegment]

    @classmethod
    def from_raw_data(
        cls,
        this_episode_slug: str,
        transcripts: Dict[Tuple[EpisodeSlug, ModelName], Transcript],
    ) -> Self:
        this_episode_transcripts = {
            model_name: transcript
            for (episode_slug, model_name), transcript in transcripts.items()
            if episode_slug == this_episode_slug
        }
        best_transcript = this_episode_transcripts.get(
            ModelName.BASE_EN, this_episode_transcripts.get(ModelName.TINY_EN, None)
        )
        if best_transcript is None:
            return cls(segments=[])
        segments = [
            CollectedSegment.from_raw_data(segment)
            for segment in best_transcript.segments
        ]
        return cls(segments=segments)


class CollectedEpisode(BaseModel):
    episode_title: str
    episode_slug: EpisodeSlug
    published: DateTime
    transcript: CollectedTranscript

    @classmethod
    def from_raw_data(
        cls,
        episode_slug: EpisodeSlug,
        episode: Episode,
        transcripts: Dict[Tuple[EpisodeSlug, ModelName], Transcript],
    ) -> Self:
        return cls(
            episode_title=episode.title,
            episode_slug=episode_slug,
            published=episode.published,
            transcript=CollectedTranscript.from_raw_data(episode_slug, transcripts),
        )


class CollectedPodcast(BaseModel):
    podcast_id: str
    podcast_title: str
    episodes: List[CollectedEpisode]

    @classmethod
    def from_raw_data(
        cls,
        this_podcast_info: PodcastInfo,
        podcast_feeds: Dict[PodcastId, PodcastFeed],
        podcast_episodes: Dict[Tuple[PodcastId, EpisodeSlug], Episode],
        transcripts: Dict[Tuple[PodcastId, EpisodeSlug, ModelName], Transcript],
    ) -> Self:
        this_podcast_id = this_podcast_info.podcast_id
        this_podcast_feed = next(
            podcast_feed
            for podcast_id, podcast_feed in podcast_feeds.items()
            if podcast_id == this_podcast_id
        )
        this_podcast_title = this_podcast_feed.title
        this_podcast_transcripts = {
            (episode_slug, model_name): transcript
            for (
                podcast_id,
                episode_slug,
                model_name,
            ), transcript in transcripts.items()
            if podcast_id == this_podcast_id
        }
        this_podcast_episodes = {
            episode_slug: CollectedEpisode.from_raw_data(
                episode_slug, episode, this_podcast_transcripts
            )
            for (podcast_id, episode_slug), episode in podcast_episodes.items()
            if podcast_id == this_podcast_id
        }
        return cls(
            podcast_id=this_podcast_id,
            podcast_title=this_podcast_title,
            episodes=list(this_podcast_episodes.values()),
        )


class CollectedData(BaseModel):
    podcasts: List[CollectedPodcast]

    @classmethod
    def from_raw_data(
        cls,
        podcast_infos: List[PodcastInfo],
        podcast_feeds: Dict[PodcastId, PodcastFeed],
        podcast_episodes: Dict[Tuple[PodcastId, EpisodeSlug], Episode],
        transcripts: Dict[Tuple[PodcastId, EpisodeSlug, ModelName], Transcript],
    ) -> Self:
        return cls(
            podcasts=[
                CollectedPodcast.from_raw_data(
                    this_podcast_info,
                    podcast_feeds,
                    podcast_episodes,
                    transcripts,
                )
                for this_podcast_info in podcast_infos
            ]
        )


def collect_data(
    podcast_infos: List[PodcastInfo],
    podcast_feeds: Dict[PodcastId, PodcastFeed],
    podcast_episodes: Dict[Tuple[PodcastId, EpisodeSlug], Episode],
    transcripts: Dict[Tuple[PodcastId, EpisodeSlug, ModelName], Transcript],
    data_folder: Path,
) -> Path:
    collected_data = CollectedData.from_raw_data(
        podcast_infos, podcast_feeds, podcast_episodes, transcripts
    )
    output_file_path = data_folder / "cleaned" / "cleaned.json"
    create_parent_folder(output_file_path)
    with open(output_file_path, "w") as f:
        f.write(collected_data.json())
    return output_file_path
