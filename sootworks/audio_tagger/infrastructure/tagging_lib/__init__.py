# -*- coding: utf-8 -*-
from sootworks.audio_tagger.infrastructure.tagging_lib._eye3d import EyeD3AudioFileTagger
from sootworks.audio_tagger.infrastructure.tagging_lib._music_tag import MusicTagAudioFileTagger


def get_supported_audio_file_extensions() -> set[str]:
    return (
        EyeD3AudioFileTagger.supported_audio_file_extentions | MusicTagAudioFileTagger.supported_audio_file_extentions
    )


__all__ = ["EyeD3AudioFileTagger", "MusicTagAudioFileTagger", "get_supported_audio_file_extensions"]
