import threading

import numpy as np
import sounddevice as sd

import config


class Recorder:
    def __init__(self, sample_rate: int = config.SAMPLE_RATE, channels: int = config.CHANNELS):
        self._sample_rate = sample_rate
        self._channels = channels
        self._lock = threading.Lock()
        self._chunks: list[np.ndarray] = []
        self._stream: sd.InputStream | None = None

    def _callback(self, indata: np.ndarray, frames: int, time_info, status):
        self._chunks.append(indata.copy())

    def start(self):
        with self._lock:
            self._chunks = []
            self._stream = sd.InputStream(
                samplerate=self._sample_rate,
                channels=self._channels,
                dtype="float32",
                callback=self._callback,
            )
            self._stream.start()

    def stop(self) -> np.ndarray:
        with self._lock:
            if self._stream is not None:
                self._stream.stop()
                self._stream.close()
                self._stream = None
            if not self._chunks:
                return np.empty(0, dtype="float32")
            audio = np.concatenate(self._chunks, axis=0).flatten()
            self._chunks = []
            return audio
