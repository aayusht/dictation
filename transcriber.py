import atexit
import io
import os
import socket
import subprocess
import time
import urllib.error
import urllib.request
import wave
from abc import ABC, abstractmethod

import numpy as np

import config


class BaseTranscriber(ABC):
    @abstractmethod
    def transcribe(self, audio: np.ndarray) -> str:
        """Convert audio samples to text."""


class _WhisperCppTranscriber(BaseTranscriber):
    """Manages a whisper-server subprocess and transcribes via its HTTP API."""

    def __init__(self):
        self._process = None
        self._base_url = f"http://{config.WHISPER_CPP_HOST}:{config.WHISPER_CPP_PORT}"
        self._start_server()
        atexit.register(self.close)

    def _start_server(self) -> None:
        cmd = [
            config.WHISPER_CPP_BIN,
            "-m",
            config.WHISPER_CPP_MODEL_PATH,
            "-l",
            config.WHISPER_LANGUAGE,
            "-t",
            str(config.WHISPER_CPP_THREADS),
            "--host",
            config.WHISPER_CPP_HOST,
            "--port",
            str(config.WHISPER_CPP_PORT),
        ]
        if config.WHISPER_CPP_NO_GPU:
            cmd.append("--no-gpu")

        env = None
        if config.IS_WINDOWS_ARM:
            env = os.environ.copy()
            msys_bin = r"C:\msys64\clangarm64\bin"
            if msys_bin not in env.get("PATH", ""):
                env["PATH"] = msys_bin + ";" + env.get("PATH", "")

        kwargs = dict(stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
        if config.IS_WINDOWS:
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

        self._process = subprocess.Popen(cmd, **kwargs)
        try:
            self._wait_for_ready()
        except Exception:
            self.close()
            raise

    def _wait_for_ready(self, timeout: float = 60.0, interval: float = 0.25) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self._process.poll() is not None:
                raise RuntimeError(
                    f"whisper-server exited unexpectedly (code {self._process.returncode})"
                )
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1.0)
                if sock.connect_ex((config.WHISPER_CPP_HOST, config.WHISPER_CPP_PORT)) == 0:
                    return
            time.sleep(interval)
        raise RuntimeError(f"whisper-server did not become ready within {timeout}s")

    def _audio_to_wav_bytes(self, audio: np.ndarray) -> bytes:
        pcm16 = (audio.clip(-1.0, 1.0) * 32767).astype("int16")
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(config.CHANNELS)
            wav_file.setsampwidth(2)
            wav_file.setframerate(config.SAMPLE_RATE)
            wav_file.writeframes(pcm16.tobytes())
        return buffer.getvalue()

    def transcribe(self, audio: np.ndarray) -> str:
        boundary = f"----whisperboundary{time.time_ns()}"
        wav_bytes = self._audio_to_wav_bytes(audio)
        body = b"".join(
            [
                (
                    f"--{boundary}\r\n"
                    'Content-Disposition: form-data; name="file"; filename="audio.wav"\r\n'
                    "Content-Type: audio/wav\r\n\r\n"
                ).encode("utf-8"),
                wav_bytes,
                b"\r\n",
                (
                    f"--{boundary}\r\n"
                    'Content-Disposition: form-data; name="response_format"\r\n\r\n'
                    "text\r\n"
                ).encode("utf-8"),
                (
                    f"--{boundary}\r\n"
                    'Content-Disposition: form-data; name="temperature"\r\n\r\n'
                    "0.0\r\n"
                ).encode("utf-8"),
                f"--{boundary}--\r\n".encode("utf-8"),
            ]
        )

        req = urllib.request.Request(
            f"{self._base_url}/inference",
            data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return resp.read().decode("utf-8", errors="replace").strip()
        except urllib.error.HTTPError as exc:
            message = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"whisper-server request failed: {exc.code} {message}") from exc
        except (urllib.error.URLError, ConnectionResetError, TimeoutError, OSError) as exc:
            raise RuntimeError(
                "whisper-server request failed; if you are on Windows ARM, keep --no-gpu enabled"
            ) from exc

    def close(self) -> None:
        if self._process and self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait()
        self._process = None


class _FasterWhisperTranscriber(BaseTranscriber):
    def __init__(self):
        from faster_whisper import WhisperModel

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


Transcriber = _WhisperCppTranscriber if config.USE_WHISPER_CPP else _FasterWhisperTranscriber
