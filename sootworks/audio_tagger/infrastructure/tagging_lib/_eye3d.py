# -*- coding: utf-8 -*-

"""eze3D only supports mp3 files with ID3 tags."""

from pathlib import Path

import eyed3

from sootworks.audio_tagger.domain.const import TagType
from sootworks.audio_tagger.domain.model import AudioTrackInfo
from sootworks.audio_tagger.domain.repository import LIB_SPECIFIC_SONG_OBJECT, IAudioTagMapper, IAudioFileTagger


TAGGING_LIB = "eye3D"
SUPPORTED_AUDIO_FILE_EXTENTIONS = {
    "mp3",
}


class _Eye3DArtistAudioTagMapper(IAudioTagMapper):
    tag_type = TagType.ARTIST
    compatible_tagging_lib = TAGGING_LIB

    def __call__(self, song: LIB_SPECIFIC_SONG_OBJECT, track_info: AudioTrackInfo) -> None:
        song.tag.artist = track_info.artist


class _Eye3DAlbumAudioTagMapper(IAudioTagMapper):
    tag_type = TagType.ALBUM
    compatible_tagging_lib = TAGGING_LIB

    def __call__(self, song: LIB_SPECIFIC_SONG_OBJECT, track_info: AudioTrackInfo) -> None:
        song.tag.album = track_info.album


class _Eye3DTitleAudioTagMapper(IAudioTagMapper):
    tag_type = TagType.TITLE
    compatible_tagging_lib = TAGGING_LIB

    def __call__(self, song: LIB_SPECIFIC_SONG_OBJECT, track_info: AudioTrackInfo) -> None:
        song.tag.title = track_info.title


class _Eye3DDateAudioTagMapper(IAudioTagMapper):
    tag_type = TagType.DATE
    compatible_tagging_lib = TAGGING_LIB

    def __call__(self, song: LIB_SPECIFIC_SONG_OBJECT, track_info: AudioTrackInfo) -> None:
        song.tag.release_date = track_info.date


class _Eye3DTrackNumbersAudioTagMapper(IAudioTagMapper):
    tag_type = TagType.TRACK_NUM
    compatible_tagging_lib = TAGGING_LIB

    def __call__(self, song: LIB_SPECIFIC_SONG_OBJECT, track_info: AudioTrackInfo) -> None:
        song.tag.track_num = (track_info.track_number, track_info.total_tracks)


class _Eye3DGenreAudioTagMapper(IAudioTagMapper):
    tag_type = TagType.GENRE
    compatible_tagging_lib = TAGGING_LIB

    def __call__(self, song: LIB_SPECIFIC_SONG_OBJECT, track_info: AudioTrackInfo) -> None:
        song.tag.genre = track_info.genre


class _Eye3DDiscsAudioTagMapper(IAudioTagMapper):
    tag_type = TagType.DISC_NUM
    compatible_tagging_lib = TAGGING_LIB

    def __call__(self, song: LIB_SPECIFIC_SONG_OBJECT, track_info: AudioTrackInfo) -> None:
        song.tag.disc_num = (track_info.disc_number, track_info.total_discs)


class _Eye3DCoverAudioTagMapper(IAudioTagMapper):
    tag_type = TagType.COVER
    compatible_tagging_lib = TAGGING_LIB

    def __call__(self, song: LIB_SPECIFIC_SONG_OBJECT, track_info: AudioTrackInfo) -> None:
        song.tag.images.set(3, track_info.cover_art_jpeg, "image/jpeg")


class Eye3DAudioFileTagger(IAudioFileTagger):
    compatible_tagging_lib = TAGGING_LIB
    supported_audio_file_extentions = SUPPORTED_AUDIO_FILE_EXTENTIONS

    @classmethod
    def get_song(cls, path: Path) -> eyed3.core.AudioFile | None:
        song = eyed3.load(path.resolve())
        if not song.tag:
            song.initTag()

        return song

    @classmethod
    def get_mappers(cls, suffix: str) -> tuple[IAudioTagMapper]:
        return (
            (
                _Eye3DArtistAudioTagMapper(),
                _Eye3DAlbumAudioTagMapper(),
                _Eye3DTitleAudioTagMapper(),
                _Eye3DDateAudioTagMapper(),
                _Eye3DTrackNumbersAudioTagMapper(),
                _Eye3DGenreAudioTagMapper(),
                _Eye3DDiscsAudioTagMapper(),
                _Eye3DCoverAudioTagMapper(),
            )
            if (suffix in cls.supported_audio_file_extentions)
            else tuple()
        )

    @classmethod
    def save_tags(cls, song: eyed3.core.AudioFile) -> None:
        song.tag.save()
