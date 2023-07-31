# -*- coding: utf-8 -*-

import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Type

from sootworks.audio_tagger.domain.const import MediumType
from sootworks.audio_tagger.domain.model import Album, AlbumInfo, AudioTrackInfo


# RegEx Patterns
FORBIDDEN_CHARACTERS = re.compile(r"[<>:\"\'\/\\|\?\*]")


class AlbumDirFormatter:
    @staticmethod
    def get_artist_dir_name(artist: str) -> str:
        return artist.replace(" ", "_")

    @staticmethod
    def get_album_dir_name(title: str, date: int) -> str:
        return f"{title.replace(' ', '_')}_({date})"

    @staticmethod
    def get_medium_dir_name(medium_number: int, medium_type: MediumType = MediumType.CD) -> str:
        match medium_type:
            case MediumType.CD:
                return f"Disc_{medium_number:02d}"
            case _:
                raise RuntimeError(f"Unsupported MediumType: {medium_type}")

    @staticmethod
    def get_audio_file_name(
        track_number: int,
        title: str,
        file_extention: str,
        medium_number: int | None = None,
        medium_type: MediumType = MediumType.CD,
    ) -> str:
        name = f"{track_number:02d}-{FORBIDDEN_CHARACTERS.sub('', title.replace(' ', '_'))}{file_extention}"

        if isinstance(medium_number, int):
            name = (
                f"{AlbumDirFormatter.get_medium_dir_name(medium_number=medium_number, medium_type=medium_type)}_-_"
                + name
                + file_extention
            )
        return name


class IAudioFileRepository(ABC):
    """Domain-level interface for implementing repositories abstracting audio file system operations."""

    def __init__(self, formatter: Type[AlbumDirFormatter]) -> None:
        self.formatter = formatter

    @abstractmethod
    def get_audio_paths(self, path: Path, suffix_filter: str | None = None) -> list[Path]:
        raise NotImplementedError()

    @staticmethod
    def _sort_track_info(album_info: AlbumInfo) -> tuple[tuple[AudioTrackInfo]]:
        stacks = [[] for i in range(album_info.total_discs)]
        for track in album_info.tracks:
            stacks[0 if (track.disc_number is None) else (track.disc_number - 1)].append(track)

        return tuple(tuple(sorted(stack, key=lambda track: track.track_number)) for stack in stacks)

    @abstractmethod
    def collate_audio_files(self, paths: list[Path]) -> Album:
        raise NotImplementedError()

    @abstractmethod
    def plan_restructuring(self, album: Album, out_path: Path) -> Album:
        raise NotImplementedError()

    @abstractmethod
    def restructure_album(self, source_structure: Album, target_structure: Album) -> None:
        raise NotImplementedError()
