# -*- coding: utf-8 -*-

from pathlib import Path

import music_tag

from sootworks.audio_tagger.domain.const import TagType
from sootworks.audio_tagger.domain.model import AudioTrackInfo
from sootworks.audio_tagger.domain.repository import LIB_SPECIFIC_SONG_OBJECT, IAudioTagMapper, IAudioFileTagger


TAGGING_LIB = "music_tag"
SUPPORTED_AUDIO_FILE_EXTENTIONS = {"aac", "aiff", "dsf", "flac", "m4a", "mp3", "ogg", "opus", "wav", "wv"}


class _MusicTagArtistAudioTagMapper(IAudioTagMapper):
    tag_type = TagType.ARTIST
    compatible_tagging_lib = TAGGING_LIB

    def __call__(self, song: LIB_SPECIFIC_SONG_OBJECT, track_info: AudioTrackInfo) -> None:
        song["artist"] = track_info.artist


class _MusicTagAlbumAudioTagMapper(IAudioTagMapper):
    tag_type = TagType.ALBUM
    compatible_tagging_lib = TAGGING_LIB

    def __call__(self, song: LIB_SPECIFIC_SONG_OBJECT, track_info: AudioTrackInfo) -> None:
        song["album"] = track_info.album


class _MusicTagTitleAudioTagMapper(IAudioTagMapper):
    tag_type = TagType.TITLE
    compatible_tagging_lib = TAGGING_LIB

    def __call__(self, song: LIB_SPECIFIC_SONG_OBJECT, track_info: AudioTrackInfo) -> None:
        song["tracktitle"] = track_info.title


class _MusicTagDateAudioTagMapper(IAudioTagMapper):
    tag_type = TagType.DATE
    compatible_tagging_lib = TAGGING_LIB

    def __call__(self, song: LIB_SPECIFIC_SONG_OBJECT, track_info: AudioTrackInfo) -> None:
        song["year"] = track_info.date


class _MusicTagTrackNumbersAudioTagMapper(IAudioTagMapper):
    tag_type = TagType.TRACK_NUM
    compatible_tagging_lib = TAGGING_LIB

    def __call__(self, song: LIB_SPECIFIC_SONG_OBJECT, track_info: AudioTrackInfo) -> None:
        song["tracknumber"], song["totaltracks"] = (track_info.track_number, track_info.total_tracks)


class _MusicTagGenreAudioTagMapper(IAudioTagMapper):
    tag_type = TagType.GENRE
    compatible_tagging_lib = TAGGING_LIB

    def __call__(self, song: LIB_SPECIFIC_SONG_OBJECT, track_info: AudioTrackInfo) -> None:
        song["genre"] = track_info.genre


class _MusicTagDiscsAudioTagMapper(IAudioTagMapper):
    tag_type = TagType.DISC_NUM
    compatible_tagging_lib = TAGGING_LIB

    def __call__(self, song: LIB_SPECIFIC_SONG_OBJECT, track_info: AudioTrackInfo) -> None:
        song["discnumber"], song["totaldiscs"] = (track_info.disc_number, track_info.total_discs)


class _MusicTagCoverAudioTagMapper(IAudioTagMapper):
    tag_type = TagType.COVER
    compatible_tagging_lib = TAGGING_LIB

    def __call__(self, song: LIB_SPECIFIC_SONG_OBJECT, track_info: AudioTrackInfo) -> None:
        song["artwork"] = track_info.cover_art_jpeg


class MusicTagAudioFileTagger(IAudioFileTagger):
    compatible_tagging_lib = TAGGING_LIB
    supported_audio_file_extentions = SUPPORTED_AUDIO_FILE_EXTENTIONS

    @classmethod
    def get_song(cls, path: Path) -> music_tag.file.AudioFile | None:
        return music_tag.load_file(path.resolve())

    @classmethod
    def get_mappers(cls, suffix: str) -> tuple[IAudioTagMapper]:
        return (
            (
                _MusicTagArtistAudioTagMapper(),
                _MusicTagAlbumAudioTagMapper(),
                _MusicTagTitleAudioTagMapper(),
                _MusicTagDateAudioTagMapper(),
                _MusicTagTrackNumbersAudioTagMapper(),
                _MusicTagGenreAudioTagMapper(),
                _MusicTagDiscsAudioTagMapper(),
                _MusicTagCoverAudioTagMapper(),
            )
            if (suffix in cls.supported_audio_file_extentions)
            else tuple()
        )

    @classmethod
    def save_tags(cls, song: music_tag.file.AudioFile) -> None:
        song.save()
