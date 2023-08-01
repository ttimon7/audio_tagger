# -*- coding: utf-8 -*-

from __future__ import annotations

from functools import wraps
from pathlib import Path
from typing import Any, Callable

import cv2 as cv
import matplotlib as mpl
import matplotlib.pyplot as plt
import musicbrainzngs
import numpy as np

from sootworks.audio_tagger.application.const import GOJIRA_FORTITUDE
from sootworks.audio_tagger.domain.model import AlbumInfo, AudioTrackInfo, DefaultTags
from sootworks.audio_tagger.domain.repository import IAlbumInfoRepository


def clean_text(text: str) -> str:
    return text.replace("’", "'")


def _set_useragent(method: Callable) -> Callable:
    @wraps(method)
    def wrapper(self, *args, **kwargs) -> Any:
        if not self._user_agent_configured:
            musicbrainzngs.set_useragent(app=self.app, version=self.version, contact=self.contact)
            self._user_agent_configured = True

        return method(self, *args, **kwargs)

    return wrapper


class MusicBrainzAlbumInfoRepository(IAlbumInfoRepository):
    def __init__(self, app: str, version: str, contact: str) -> None:
        self.app = app
        self.version = version
        self.contact = contact

        self._user_agent_configured = False

    @_set_useragent
    def query_album_id(self, album_name: str, artist: str | None = None, year: int | None = None) -> str:
        """FIXME implement me"""
        return GOJIRA_FORTITUDE

    @_set_useragent
    def _has_approved_cover_art(self, album_id: str) -> bool:
        data = musicbrainzngs.get_image_list(album_id)

        match = False
        for image in data["images"]:
            if "Front" in image["types"] and image["approved"]:
                print(f"{image['thumbnails']['large']} is an approved front image!")

                match = True
                break

        return match

    @_set_useragent
    def get_cover_art(self, album_id: str, default_cover_art: Path | None) -> np.ndarray | None:
        cover_art = None
        if default_cover_art is None:
            if self._has_approved_cover_art(album_id=album_id):
                raw_image = musicbrainzngs.get_image_front(releaseid=album_id)

                np_image_array = np.frombuffer(raw_image, np.uint8)
                cover_art = cv.imdecode(np_image_array, cv.IMREAD_COLOR)
            else:
                print(f"No approved cover image found for album: '{album_id}'")
        else:
            cover_art = cv.imread(str(default_cover_art))

        return cover_art

    @_set_useragent
    def _verify_cover_art(self, cover_art: np.ndarray | None) -> None:
        key_pressed = [None]
        if cover_art is not None:
            window_name = "Cover Art"

            # Disabling matplotlib toolbar on figure.
            mpl.rcParams["toolbar"] = "None"

            def handle_key_press(event):
                key_pressed[0] = event.key.lower()

                match key_pressed[0]:
                    case "y":
                        plt.close()
                    case "n":
                        plt.close()
                    case _:
                        print("Try again (possible choices: ['y', 'n'])")

            def show_image(image: np.ndarray) -> None:
                fig = plt.figure(num=window_name, frameon=False, figsize=[5, 5])
                # removing margins around plot (https://stackoverflow.com/questions/14908576/how-to-remove-frame-from-a-figure)
                ax = fig.add_axes([0, 0, 1, 1])
                ax.axis("off")  # removing axes
                fig.canvas.mpl_connect("key_press_event", handle_key_press)
                ax.imshow(cv.cvtColor(image, cv.COLOR_BGR2RGB))
                plt.show()

            while key_pressed[0] not in ["y", "n"]:
                show_image(image=cover_art)

        return key_pressed[0] == "y"

    @_set_useragent
    def _parse_musicbrainz_release_descriptor(self, info: dict, default_tags: DefaultTags) -> AlbumInfo:
        release = info["release"]

        def get_artists(release: dict) -> str:
            artists = []
            for artist_info in release["artist-credit"]:
                if isinstance(artist_info, dict):
                    artists.append(artist_info["artist"]["name"])

            return ", ".join(artists)

        def get_tracks(release: dict, album_info: AlbumInfo) -> list[AudioTrackInfo]:
            tracks = []
            for disc_number, medium in enumerate(release["medium-list"], start=1):
                for track_info in medium["track-list"]:
                    tracks.append(
                        AudioTrackInfo(
                            album_info=album_info,
                            title=clean_text(track_info["recording"]["title"]),
                            total_tracks=len(medium["track-list"]),
                            track_number=track_info["position"],
                            # TODO fetch genre
                            disc_number=None if (album_info.total_discs == 1) else disc_number,
                        )
                    )

            return tracks

        album_info = AlbumInfo(
            title=clean_text(release["title"]),
            artist=clean_text(get_artists(release)),
            date=int(release["date"][:4]),
            total_discs=release["medium-count"],
        )

        cover_art = self.get_cover_art(album_id=release["id"], default_cover_art=default_tags.cover_art)
        if self._verify_cover_art(cover_art=cover_art):
            album_info.cover_art = cover_art

        album_info.tracks = get_tracks(release=release, album_info=album_info)

        return album_info

    @_set_useragent
    def get_album_info(self, album_id: str, default_tags: DefaultTags) -> AlbumInfo:
        try:
            info = musicbrainzngs.get_release_by_id(album_id, includes=["artists", "recordings"])
        except musicbrainzngs.WebServiceError as e:
            print(f"Something went wrong with the request: {e}")
        else:
            return self._parse_musicbrainz_release_descriptor(info=info, default_tags=default_tags)
