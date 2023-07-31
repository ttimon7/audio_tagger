# -*- coding: utf-8 -*-

"""Application-level constants

Mostly default values...
"""

from enum import Enum


class MediumType(Enum):
    # TODO add support for other media types
    CD = "CD"


class TagType(Enum):
    ARTIST = "ARTIST"
    ALBUM = "ALBUM"
    TITLE = "TITLE"
    DATE = "DATE"
    TRACK_NUM = "TRACK_NUM"
    GENRE = "GENRE"
    DISC_NUM = "DISC_NUM"
    COVER = "COVER"
