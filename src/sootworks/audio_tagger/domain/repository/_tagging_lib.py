# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from sootworks.audio_tagger.domain.const import TagType
from sootworks.audio_tagger.domain.model import AudioTrackInfo


# Type definitions
LIB_SPECIFIC_SONG_OBJECT = Any


class IAudioTagMapper(ABC):
    tag_type: TagType
    compatible_tagging_lib: str

    @abstractmethod
    def __call__(self, song: LIB_SPECIFIC_SONG_OBJECT, track_info: AudioTrackInfo) -> None:
        pass


class IAudioFileTagger(ABC):
    compatible_tagging_lib: str
    supported_audio_file_extentions: set[str]

    @classmethod
    @abstractmethod
    def get_song(cls, path: Path) -> Any:
        pass

    @classmethod
    @abstractmethod
    def get_mappers(cls, suffix: str) -> tuple[IAudioTagMapper]:
        pass

    @classmethod
    @abstractmethod
    def save_tags(cls, song: Any) -> None:
        pass
