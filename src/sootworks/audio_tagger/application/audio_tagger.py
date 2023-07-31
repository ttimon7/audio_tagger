# -*- coding: utf-8 -*-


import io
from pathlib import Path

from termcolor import colored

from sootworks.audio_tagger.application.exceptions import AudioTaggingCancelled
from sootworks.audio_tagger.application.specification import IAlbumTagger
from sootworks.audio_tagger.domain.model import Album, AlbumInfo, AlbumQueryParams, AudioMedium, DefaultTags
from sootworks.audio_tagger.domain.repository import IAlbumInfoRepository, IAudioFileRepository, IAudioFileTagger


class SimpleAlbumTagger(IAlbumTagger):
    def __init__(
        self,
        album_info_repo: IAlbumInfoRepository,
        audio_file_repo: IAudioFileRepository,
        taggers: tuple[IAudioFileTagger],
        suffix_filter: str,
    ) -> None:
        self.album_info_repo = album_info_repo
        self.audio_file_repo = audio_file_repo
        self.taggers = taggers
        self.suffix_filter = suffix_filter

    def _update_album_info(self, info: AlbumInfo, default_tags: DefaultTags) -> None:
        for track in info.tracks:
            track.genre = track.genre if default_tags.genre is None else default_tags.genre
            track.disc_number = track.disc_number if default_tags.disc_number is None else default_tags.disc_number
            track.comment = track.comment if default_tags.comment is None else default_tags.comment

    def _get_album_info(self, album_query_params: AlbumQueryParams, default_tags: DefaultTags) -> AlbumInfo:
        album_id = self.album_info_repo.get_album_id(album_query_params=album_query_params)
        album_info = self.album_info_repo.get_album_info(album_id=album_id, default_tags=default_tags)
        self._update_album_info(info=album_info, default_tags=default_tags)

        return album_info

    def _parse_audio_source(self, in_path: Path, album_info: AlbumInfo) -> Album:
        source_audio_files = self.audio_file_repo.get_audio_paths(path=in_path, suffix_filter=self.suffix_filter)
        album = self.audio_file_repo.collate_audio_files(paths=source_audio_files, album_info=album_info)

        return album

    @staticmethod
    def _get_parent_paths(source_medium: AudioMedium, target_medium: AudioMedium) -> tuple[str, ...]:
        split_path = lambda path: str(path).split("/")  # noqa: E731
        join_parts = lambda parts: "/".join(parts)  # noqa: E731

        src_parts = split_path(source_medium.paths[0].parent.resolve())
        tgt_parts = split_path(target_medium.paths[0].parent.resolve())
        common, src_diff, tgt_diff = [], [], []
        for i in range(len(src_parts)):
            if len(tgt_parts) > i:
                if src_parts[i] != tgt_parts[i]:
                    src_diff += src_parts[i:]
                    tgt_diff += tgt_parts[i:]
                    break
                else:
                    common.append(src_parts[i])
            else:
                tgt_diff += tgt_parts[i:]
                break

        return join_parts(common), join_parts(src_diff), join_parts(tgt_diff)

    @staticmethod
    def _add_dir_locations_to_comparison(
        buffer: io.StringIO, disc_number: int, source_medium: AudioMedium, target_medium: AudioMedium
    ) -> None:
        common, src_diff, tgt_diff = SimpleAlbumTagger._get_parent_paths(
            source_medium=source_medium, target_medium=target_medium
        )

        buffer.write(f"\n  Disc {disc_number:02d})\n    * copying files:")
        buffer.write(f"\n      * from: {common}/{colored(src_diff, 'light_cyan', attrs=['bold'])}")
        buffer.write(f"\n      * to:   {common}/{colored(tgt_diff, 'light_magenta', attrs=['bold'])}")

    @staticmethod
    def _add_file_names_to_comparison(
        buffer: io.StringIO, source_medium: AudioMedium, target_medium: AudioMedium
    ) -> None:
        buffer.write("\n    * file names:")
        for i in range(len(source_medium.paths)):
            src_name, tgt_name = source_medium.paths[i].name, target_medium.paths[i].name
            buffer.write(f"\n      Track {(i + 1):02d}:")
            buffer.write(f"\n        * old: {colored(src_name, 'light_cyan', attrs=['bold'])}")
            buffer.write(f"\n        * new: {colored(tgt_name, 'light_magenta', attrs=['bold'])}")

    def _verify_restructuring(self, source_structure: Album, target_structure: Album) -> None:
        """Presenting the old and new dir structure to the user for comparison, asking for verification."""
        buffer = io.StringIO()
        buffer.write(colored("\n+++ Summary +++\n", attrs=["bold"]))
        for medium_index in range(len(source_structure.media)):
            source_medium, target_medium = source_structure.media[medium_index], target_structure.media[medium_index]

            SimpleAlbumTagger._add_dir_locations_to_comparison(
                buffer=buffer, disc_number=(medium_index + 1), source_medium=source_medium, target_medium=target_medium
            )

            SimpleAlbumTagger._add_file_names_to_comparison(
                buffer=buffer, source_medium=source_medium, target_medium=target_medium
            )

        print(buffer.getvalue())

        user_input = input("\nLooks good? (y/N)").lower()
        while user_input not in ("", "y", "n"):
            user_input = input("\nLooks good? (y/N)").lower()

        if not user_input == "y":
            raise AudioTaggingCancelled("restructuring strategy has been refused by user.")

    def _restructure_album(self, album: Album, out_path: Path) -> Album:
        """Making a copy of the audio files under a new dir structure matching the configured format."""
        target_structure: Album = self.audio_file_repo.plan_restructuring(album=album, out_path=out_path)

        # NOTE tested till here

        self._verify_restructuring(source_structure=album, target_structure=target_structure)
        self.audio_file_repo.restructure_album(source_structure=album, target_structure=target_structure)

        return target_structure

    def _perform_tagging(self, album: Album) -> None:
        """Setting metadata on the restructured album."""
        for track_info in album.info.tracks:
            medium_index, path_index = (0 if (track_info.disc_number is None) else (track_info.disc_number - 1)), (
                track_info.track_number - 1
            )
            path = album.media[medium_index].paths[path_index]
            suffix = path.suffix[1:]

            processed = False
            for tagger in self.taggers:
                if suffix in tagger.supported_audio_file_extentions:
                    song = tagger.get_song(path=path)
                    for mapper in tagger.get_mappers(suffix=suffix):
                        mapper(song=song, track_info=track_info)

                    tagger.save_tags(song=song)

                    processed = True
            if not processed:
                raise RuntimeError(f"Unsupported media format encountered: {suffix}")

    def tag_album(
        self, in_path: Path, album_query_params: AlbumQueryParams, default_tags: DefaultTags, out_path: Path
    ) -> None:
        album_info = self._get_album_info(album_query_params=album_query_params, default_tags=default_tags)
        album = self._parse_audio_source(in_path=in_path, album_info=album_info)
        restructured_album = self._restructure_album(album=album, out_path=out_path)
        self._perform_tagging(album=restructured_album)
