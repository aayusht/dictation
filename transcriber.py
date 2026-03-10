import numpy as np
from faster_whisper import WhisperModel

import config


class Transcriber:
    def __init__(self):
        self.model = WhisperModel(
            config.WHISPER_MODEL_SIZE,
            device=config.WHISPER_DEVICE,
            compute_type=config.WHISPER_COMPUTE_TYPE,
        )

    def transcribe(self, audio: np.ndarray) -> str:
        segments, _ = self.model.transcribe(
            audio,
            beam_size=config.WHISPER_BEAM_SIZE,
            language=config.WHISPER_LANGUAGE,
            vad_filter=config.WHISPER_VAD_FILTER,
        )
        return " ".join(seg.text.strip() for seg in segments)
