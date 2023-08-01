# -*- coding: utf-8 -*-
import tomllib

from pathlib import Path
from pytest import fixture

from pydantic import BaseModel


ALBUMS_CONFIG_PATH = Path("tests/config/albums.toml")


class AlbumMediaConfig(BaseModel):
    dir_name: str | None = None
    files: list[Path]


class AlbumConfig(BaseModel):
    title: str
    cover_art: str
    media: list[AlbumMediaConfig]


def _load_album_configs() -> list[AlbumConfig]:
    album_configs = []
    with ALBUMS_CONFIG_PATH.open("rb") as f:
        for raw_album_config in tomllib.load(f)["albums"]:
            album_configs.append(AlbumConfig(**raw_album_config))

    return album_configs


def _provision_albums(album_configs: list[AlbumConfig]) -> dict[str, Path]:
    pass


def _clean_up_albums(album_paths: list[Path]) -> None:
    pass


@fixture(scope="session")
def albums() -> dict[str, Path]:
    album_configs = _load_album_configs()
    album_paths = _provision_albums(album_configs=album_configs)

    yield album_paths

    _clean_up_albums(album_paths=album_paths)
