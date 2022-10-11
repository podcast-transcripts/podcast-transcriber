import json
from pathlib import Path
from typing import Any, Dict

import whisper

from podcast_transcriber.types import (
    EpisodeSlug,
    ModelName,
    NamedModel,
    PodcastId,
    Transcript,
)
from podcast_transcriber.utils import create_parent_folder


def get_model(model_name: ModelName) -> NamedModel:
    return NamedModel(name=model_name, model=whisper.load_model(model_name))


def transcribe_file(audio_file: Path, model: NamedModel) -> Transcript:
    transcript_dict: Dict[str, Any] = model.model.transcribe(  # type: ignore
        str(audio_file.resolve()), language="en"
    )
    return Transcript(**transcript_dict)


def get_transcript_file_path(
    podcast_id: PodcastId,
    episode_slug: EpisodeSlug,
    model_name: ModelName,
    data_folder: Path,
) -> Path:
    return (
        data_folder
        / "raw"
        / "transcripts"
        / podcast_id
        / episode_slug
        / (model_name + ".json")
    )


def read_transcript_file(file_path: Path) -> Transcript:
    with open(file_path, "r") as f:
        print(f"Reading transcript from `{file_path.resolve()}`.")
        return Transcript(**json.load(f))


def transcribe_episode(
    podcast_id: PodcastId,
    episode_slug: EpisodeSlug,
    episode_audio_file: Path,
    model: NamedModel,
    data_folder: Path,
) -> Transcript:
    transcript_file_path = get_transcript_file_path(
        podcast_id, episode_slug, model.name, data_folder
    )
    try:
        transcript = read_transcript_file(transcript_file_path)

    except FileNotFoundError:
        print(f"Transcribing `{episode_audio_file.resolve()}`.")
        transcript = transcribe_file(episode_audio_file, model)
        print(f"Writing transcript to `{transcript_file_path.resolve()}`.")
        create_parent_folder(transcript_file_path)
        with open(transcript_file_path, "w") as f:
            f.write(transcript.json())

    return transcript
