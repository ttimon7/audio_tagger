# -*- coding: utf-8 -*-

import re
import shutil

from collections import deque
from functools import reduce
from pathlib import Path

from sootworks.audio_tagger.infrastructure.tagging_lib import get_supported_audio_file_extensions
from sootworks.audio_tagger.domain.const import MediumType
from sootworks.audio_tagger.domain.exceptions import AlbumInfoValidationError
from sootworks.audio_tagger.domain.model import Album, AlbumInfo, AudioMedium, AudioTrackInfo
from sootworks.audio_tagger.domain.repository import IAudioFileRepository


MEDIUM_NUMBER_PATTERN = re.compile(".*((disc|cd|vinyl)[ _-]*)([0-9]{1,2}).*", re.IGNORECASE)


class SimpleAudioFileRepository(IAudioFileRepository):
    def get_audio_paths(self, path: Path, suffix_filter: str | None = None) -> list[Path]:
        audio_paths = []
        stack = deque([path])
        try:
            while parent := stack.pop():
                for candidate in parent.iterdir():
                    suffix = candidate.suffix[1:]  # excluding leading period
                    if candidate.is_dir():
                        stack.append(candidate)
                    elif suffix in get_supported_audio_file_extensions():
                        if isinstance(suffix_filter, str) and (suffix != suffix_filter):
                            continue
                        audio_paths.append(candidate)
        except IndexError:
            pass

        return audio_paths

    def _get_medium_type(self, album_info: AlbumInfo) -> MediumType:
        return MediumType.CD  # FIXME Derive media type from album info

    def _verify_media_count(self, album: Album) -> None:
        # Only counting media with associated paths.
        media_with_path = len(list(filter(lambda medium: len(medium.paths) > 0, album.media)))
        if media_with_path != album.info.total_discs:
            raise AlbumInfoValidationError(
                f"Album media count with path set ({media_with_path})"
                f" doesn't match expectation ({album.info.total_discs})."
            )

    def _get_medium_track_count(self, i: int, tracks: AudioTrackInfo, medium_count: int) -> int:
        return (
            reduce(lambda acc, track: (acc + 1 if track.disc_number == i else acc), tracks, 0)
            if medium_count > 1
            else len(tracks)
        )

    def _verify_track_count(self, album: Album) -> None:
        for i, medium in enumerate(album.media, start=1):
            medium_track_count = self._get_medium_track_count(
                i=i, tracks=album.info.tracks, medium_count=album.info.total_discs
            )
            if len(medium.paths) != medium_track_count:
                raise AlbumInfoValidationError(
                    f"Album medium track count ({len(medium.paths)} for medium '{i}')"
                    f" doesn't match expectation ({medium_track_count})."
                )

    def _verify_album_info(self, album: Album) -> None:
        self._verify_media_count(album=album)
        self._verify_track_count(album=album)

    def _get_medium_number(self, path: Path) -> int:
        medium_number = 1
        match = MEDIUM_NUMBER_PATTERN.findall(str(path.parent.name))
        if (len(match) > 0) and (len(match[0]) == 3):
            medium_number = int(match[0][2])

        return medium_number

    def collate_audio_files(self, paths: list[Path], album_info: AlbumInfo) -> Album:
        album = Album(info=album_info)

        media = [AudioMedium(type=self._get_medium_type(album_info)) for i in range(album_info.total_discs)]
        for path in sorted(paths, key=lambda path: str(path)):
            medium_index = self._get_medium_number(path) - 1
            media[medium_index].paths.append(path)

        album.media = media

        self._verify_album_info(album=album)

        return album

    def _get_out_base_path(self, album: Album, out_path: Path) -> Path:
        artis_dir = out_path / self.formatter.get_artist_dir_name(artist=album.info.artist)
        base_path = artis_dir / self.formatter.get_album_dir_name(title=album.info.title, date=album.info.date)

        return base_path

    def _get_medium_out_path(self, base_path: Path, medium_number: int, single_medium_album: bool = True) -> Path:
        return (
            base_path
            if single_medium_album
            else (base_path / self.formatter.get_medium_dir_name(medium_number=medium_number))  # FIXME add MediumType
        )

    def plan_restructuring(self, album: Album, out_path: Path) -> Album:
        target_structure = Album(info=album.info)

        single_medium_album = album.info.total_discs == 1
        track_info = self._sort_track_info(album_info=album.info)
        base_path = self._get_out_base_path(album=album, out_path=out_path)
        for medium_number, tracks in enumerate(track_info, start=1):
            # By this point both track info and media must have been sorted.

            new_medium = AudioMedium(type=MediumType.CD)  # FIXME, make type adjustable
            target_structure.media.append(new_medium)

            medium_path = self._get_medium_out_path(
                base_path=base_path, medium_number=medium_number, single_medium_album=single_medium_album
            )
            for track_number, track in enumerate(tracks, start=1):
                # match album info to tracks (rename tracks)
                file_extention = album.media[(medium_number - 1)].paths[(track_number - 1)].suffix
                new_path = medium_path / self.formatter.get_audio_file_name(
                    track_number=track_number,
                    title=track.title,
                    file_extention=file_extention,
                    medium_number=track.disc_number,
                )
                new_medium.paths.append(new_path)

        return target_structure

    def restructure_album(self, source_structure: Album, target_structure: Album) -> None:
        for medium_index in range(len(source_structure.media)):
            src_paths, tgt_paths = (
                source_structure.media[medium_index].paths,
                target_structure.media[medium_index].paths,
            )

            # Create target dir
            tgt_paths[0].parent.resolve().mkdir(parents=True, exist_ok=True)

            # Copy files
            for path_index in range(len(src_paths)):
                shutil.copy2(src_paths[path_index], tgt_paths[path_index])
