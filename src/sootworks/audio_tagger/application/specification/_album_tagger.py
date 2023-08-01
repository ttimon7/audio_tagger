# -*- coding: utf-8 -*-

"""Specification of an album tagging service aimed at automating the process of tagging
audio files in the context of an album fo that they become easily recognizable by media
servers such as Emby, Kodi, and Plex."""

from abc import ABC, abstractmethod
from pathlib import Path


from sootworks.audio_tagger.domain.model import AlbumQueryParams, DefaultTags


class IAlbumTagger(ABC):
    @abstractmethod
    def tag_album(
        self, in_path: Path, album_query_params: AlbumQueryParams, default_tags: DefaultTags, out_path: Path
    ) -> None:
        album_info = self._get_album_info(album_query_params=album_query_params, default_tags=default_tags)
        album = self._parse_audio_source(in_path=in_path, album_info=album_info)
        restructured_album = self._restructure_album(album=album, out_path=out_path)
        self._perform_tagging(album=restructured_album)
