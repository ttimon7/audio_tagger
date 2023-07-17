# -*- coding: utf-8 -*-

"""Application entry point.
"""

from argparse import ArgumentParser
from pathlib import Path

from sootworks.audio_tagger.application.const import APP, VERSION, CONTACT
from sootworks.audio_tagger.infrastructure.tagging_lib import Eye3DAudioFileTagger, MusicTagAudioFileTagger
from sootworks.audio_tagger.infrastructure.album_info import MusicBrainzAlbumInfoRepository
from sootworks.audio_tagger.infrastructure.audio_file import SimpleAudioFileRepository
from sootworks.audio_tagger.application.audio_tagger import SimpleAlbumTagger
from sootworks.audio_tagger.application.exceptions import AudioTaggingCancelled
from sootworks.audio_tagger.domain.model import AlbumQueryParams, DefaultTags
from sootworks.audio_tagger.domain.repository import AlbumDirFormatter, IAudioTagMapper


# Type declarations
InPath = OutPath = Path
SuffixFilter = str


def parse_args() -> tuple[InPath, AlbumQueryParams, DefaultTags, SuffixFilter, OutPath]:
    parser = ArgumentParser(description=("Tagging audio recordings."))
    parser.add_argument("path", type=Path, help="absolute path of the album directory")
    parser.add_argument("-n", "--album-name", help="the name of the album")
    parser.add_argument("-a", "--album-artist", dest="artist", help="the name of the album artist")
    parser.add_argument("-y", "--album-year-of-release", dest="year", help="the release year of the album")
    parser.add_argument("-i", "--album-id", help="the MusicBrainz release ID")
    parser.add_argument(
        "-g",
        "--genre",
        help=(
            "a single name or a colon-separated list of genres. If required, this must be given manually as genre"
            " info is not fetched automatically by the tagger."
        ),
    )
    parser.add_argument(
        "-c",
        "--cover-art",
        type=Path,
        help="absolute path of the cover image to set",
    )
    parser.add_argument(
        "-d",
        "--disc-number",
        type=int,
        help=(
            "the disk number to use. Useful for sources where each disk of an album has been separated"
            " to different directories of the same level rather than being grouped under the album dir."
        ),
    )
    parser.add_argument(
        "-s",
        "--suffix-filter",
        help="only those audio files will be process which have a matching file extension.",
    )
    parser.add_argument("--comment", help="a comment to add to all track metadata tags.")
    parser.add_argument(
        "-o", "--output", type=Path, default=Path("."), help="the dir to which the tagged audio files are to be written"
    )

    args = parser.parse_args()

    album_query_params = AlbumQueryParams(
        album_id=args.album_id,
        album_name=args.album_name,
        artist=args.artist,
        year=args.year,
    )

    default_tags = DefaultTags(
        genre=args.genre,
        cover_art=args.cover_art,
        disc_number=args.disc_number,
        comment=args.comment,
    )

    return args.path, album_query_params, default_tags, args.suffix_filter, args.output


def get_mappers() -> dict[str, tuple[IAudioTagMapper]]:
    return {
        MusicTagAudioFileTagger.compatible_tagging_lib: MusicTagAudioFileTagger.get_mappers(),  # preferred
        Eye3DAudioFileTagger.compatible_tagging_lib: Eye3DAudioFileTagger.get_mappers(),
    }


def main() -> None:
    in_path, album_query_params, default_tags, suffix_filter, out_path = parse_args()

    album_info_repo = MusicBrainzAlbumInfoRepository(app=APP, version=VERSION, contact=CONTACT)
    audio_file_repo = SimpleAudioFileRepository(formatter=AlbumDirFormatter)
    tagger = SimpleAlbumTagger(
        album_info_repo=album_info_repo,
        audio_file_repo=audio_file_repo,
        taggers=(MusicTagAudioFileTagger, Eye3DAudioFileTagger),
        suffix_filter=suffix_filter,
    )
    try:
        tagger.tag_album(
            in_path=in_path, album_query_params=album_query_params, default_tags=default_tags, out_path=out_path
        )
    except AudioTaggingCancelled as e:
        print(f"Exiting due to {e}")
        exit(0)


if __name__ == "__main__":
    main()
