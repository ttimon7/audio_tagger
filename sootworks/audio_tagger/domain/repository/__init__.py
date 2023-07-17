# -*- coding: utf-8 -*-

"""Domain Repositories

The repository pattern is a design pattern that provides a way to abstract the data
access layer in an application. It acts as an intermediary between an application's
data access layer and business logic layer, effectively decoupling the two.

A repository is typically implemented as a class containing methods for performing
CRUD (create, read, update, and delete) operations on a particular entity type. The
methods in a repository typically return domain objects rather than data transfer
objects or data access objects, which allows the business logic layer to work with
objects specific to the problem domain rather than objects specific to the data
access technology being used.
"""

from sootworks.audio_tagger.domain.repository._album_info import IAlbumInfoRepository
from sootworks.audio_tagger.domain.repository._audio_file import AlbumDirFormatter, IAudioFileRepository
from sootworks.audio_tagger.domain.repository._tagging_lib import (
    LIB_SPECIFIC_SONG_OBJECT,
    IAudioTagMapper,
    IAudioFileTagger,
)

__all__ = [
    "AlbumDirFormatter",
    "IAlbumInfoRepository",
    "IAudioFileRepository",
    "IAudioTagMapper",
    "IAudioFileTagger",
    "LIB_SPECIFIC_SONG_OBJECT",
]
