# -*- coding: utf-8 -*-

"""Domain Models

The most stable Domain Entities used for exchanging information between Domain Services.
"""

# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

import cv2 as cv
import numpy as np
from pydantic import BaseModel, Field, PrivateAttr

from sootworks.audio_tagger.domain.const import MediumType


class AlbumQueryParams(BaseModel):
    album_id: str | None = None
    album_name: str | None = None
    artist: str | None = None
    year: int | None = None


class DefaultTags(BaseModel):
    genre: str | None = None
    cover_art: Path | None = None
    disc_number: int | None = None
    comment: str | None = None


class AlbumInfo(BaseModel):
    title: str  # e.g. Vovin
    artist: str  # e.g. Therion
    date: int  # e.g. 1998
    tracks: list[AudioTrackInfo] = Field(default_factory=list)
    # cover_art is an image buffer to be loaded by np.frombuffer(cover_art, np.uint8)
    cover_art: np.ndarray | None = None
    total_discs: int = 1  # 1

    _cover_art_jpeg: bytes | None = PrivateAttr(default_factory=lambda: None)

    @property
    def cover_art_jpeg(self) -> bytes | None:
        if (self.cover_art is not None) and (self._cover_art_jpeg is None):
            self._cover_art_jpeg = cv.imencode(".jpg", self.cover_art)[1].tobytes()

        return self._cover_art_jpeg

    class Config:
        # FIXME PyDantic can't handle Numpy values when performing type checking.
        arbitrary_types_allowed = True


class AudioTrackInfo(BaseModel):
    album_info: AlbumInfo
    title: str  # e.g. The Rise of Sodom and Gomorrah
    total_tracks: int  # e.g. 12
    track_number: int  # e.g. 1
    genre: str | None = None  # metal
    disc_number: int | None = None  # e.g. 1
    comment: str | None = None  # e.g. Special Edition

    @property
    def album(self) -> str:
        return self.album_info.title

    @property
    def artist(self) -> str:
        return self.album_info.artist

    @property
    def date(self) -> int:
        return self.album_info.date

    @property
    def cover_art(self) -> np.ndarray | None:
        return self.album_info.cover_art

    @property
    def cover_art_jpeg(self) -> bytes | None:
        return self.album_info.cover_art_jpeg

    @property
    def total_discs(self) -> int:
        return self.album_info.total_discs

    @classmethod
    def from_album_track_info(cls, other: AudioTrackInfo) -> AudioTrackInfo:
        return cls(
            album_info=other.album_info,
            title=other.title,
            track_number=other.track_number,
            genre=other.genre,
            disc_number=other.disc_number,
            comment=other.comment,
        )


class AudioMedium(BaseModel):
    type: MediumType
    paths: list[Path] = Field(default_factory=list)

    @property
    def total_tracks(self) -> int:
        return len(self.paths)


class Album(BaseModel):
    info: AlbumInfo | None = None
    media: list[AudioMedium] = Field(default_factory=list)  # Media should be in order (i.e. CD 1, CD 2, ...)
