# -*- coding: utf-8 -*-
from sootworks.audio_tagger.infrastructure.tagging_lib._eye3d import Eye3DAudioFileTagger
from sootworks.audio_tagger.infrastructure.tagging_lib._music_tag import MusicTagAudioFileTagger


def get_supported_audio_file_extensions() -> set[str]:
    return (
        Eye3DAudioFileTagger.supported_audio_file_extentions | MusicTagAudioFileTagger.supported_audio_file_extentions
    )


__all__ = ["Eye3DAudioFileTagger", "MusicTagAudioFileTagger", "get_supported_audio_file_extensions"]
