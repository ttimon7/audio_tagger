# Audio Tagger

A productivity tool for automating the process of tagging audio files of an album, with the aim of making them properly recognized by media servers such as Emby, Kodi, and Plex.

## Motivation

It is often difficult to acquire music that is properly tagged, even when dealing with trusted sources. Without proper tagging and files organized in a specific manner, media services often fail to properly recognize the media content, or present it as intended. I've found multi-disc albums especially problematic, since when improperly tagged, media servers often mix and match albums and tracks.

Manually tagging hundreds of albums can rapidly become burdensome to the degree that one gives up the good fight, and since I don't particularly enjoy menial work of this kind I sought a way to automate the process. I've tried different open-source solutions, but even the best I could find, the ever so lovely [Kid3](https://kid3.kde.org) couldn't fulfill my needs.

I was looking for something simple, but with the capability of fetching tag information from different online encyclopedias, and organizing my collection following a unified dir structure and file naming convention that makes finding particular recording a breeze, while further eases identification of the recordings. Moreover, I needed something modular, and flexible enough so that backend components can easily be added/switched out when needed.

## Features

* Edit all versions of ID3v2 tags, and parse all standard ID3v2.4 frames (thanks to [Mutagen](https://mutagen.readthedocs.io/en/latest/))
* Fetch tag information and cover art dynamically from [MisicBrainz](https://musicbrainz.org) (a release ID must be provided)
* Restructure album content (the output format is not adjustable for the moment, if such a feature is required enthusiastic contributions are welcome - see [guideline](#Contribution-Guidelines))

## Usage

```bash
usage: __main__.py [-h] [-n ALBUM_NAME] [-a ARTIST] [-y YEAR] [-i ALBUM_ID] [-g GENRE] [-c COVER_ART] [-d DISC_NUMBER] [-s SUFFIX_FILTER]
                   [--comment COMMENT] [-o OUTPUT]
                   path

Tagging audio recordings.

positional arguments:
  path                  absolute path of the album directory

options:
  -h, --help            show this help message and exit
  -n ALBUM_NAME, --album-name ALBUM_NAME
                        the name of the album
  -a ARTIST, --album-artist ARTIST
                        the name of the album artist
  -y YEAR, --album-year-of-release YEAR
                        the release year of the album
  -i ALBUM_ID, --album-id ALBUM_ID
                        the MusicBrainz release ID
  -g GENRE, --genre GENRE
                        a single name or a colon-separated list of genres. If required, this must be given manually as genre info is not
                        fetched automatically by the tagger.
  -c COVER_ART, --cover-art COVER_ART
                        absolute path of the cover image to set
  -d DISC_NUMBER, --disc-number DISC_NUMBER
                        the disk number to use. Useful for sources where each disk of an album has been separated to different directories
                        of the same level rather than being grouped under the album dir.
  -s SUFFIX_FILTER, --suffix-filter SUFFIX_FILTER
                        only those audio files will be process which have a matching file extension.
  --comment COMMENT     a comment to add to all track metadata tags.
  -o OUTPUT, --output OUTPUT
                        the dir to which the tagged audio files are to be written
```

### Example Invocation

```bash
python3.11 -m audio_tagger \
    "/path/to/album/dir" \
    -i="<MUSICBRAINZ_RELEASE_ID>" \
    -g="<COMMA_SEPARATED_LIST_OF_GENRES>" \
    -c="/path/to/album/cover.jpg"
```

## Contribution Guidelines

TODO
