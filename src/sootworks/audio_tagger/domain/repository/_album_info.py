# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod

from sootworks.audio_tagger.domain.model import AlbumInfo, AlbumQueryParams, DefaultTags


class IAlbumInfoRepository(ABC):
    """Domain-level interface for implementing repositories abstracting album information management."""

    def get_album_id(self, album_query_params: AlbumQueryParams) -> str:
        return (
            self.query_album_id(
                album_name=album_query_params.album_name, artist=album_query_params.artist, year=album_query_params.year
            )
            if album_query_params.album_id is None
            else album_query_params.album_id
        )

    @abstractmethod
    def query_album_id(self, album_name: str, artist: str | None = None, year: int | None = None) -> str:
        raise NotImplementedError()

    @abstractmethod
    def get_cover_art(self, album_id: str) -> bytes | None:
        raise NotImplementedError()

    @abstractmethod
    def get_album_info(self, album_id: str, default_tags: DefaultTags) -> AlbumInfo:
        raise NotImplementedError()
