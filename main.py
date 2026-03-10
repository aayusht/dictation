import threading

import numpy as np
import sounddevice as sd

import config
import injector
from hotkey import HotkeyListener
from post_process import post_process
from recorder import Recorder
from rewriter import Rewriter
from transcriber import Transcriber


def _beep(freq: float) -> None:
    if not config.BEEP_ENABLED:
        return
    duration = config.BEEP_DURATION_MS / 1000.0
    t = np.linspace(0, duration, int(config.SAMPLE_RATE * duration), endpoint=False, dtype="float32")
    wave = 0.3 * np.sin(2 * np.pi * freq * t)
    sd.play(wave, samplerate=config.SAMPLE_RATE)


def main():
    print("Loading transcriber…")
    transcriber = Transcriber()
    print("Loading rewriter…")
    rewriter = Rewriter()
    print("Models loaded. Press F9 to dictate.")

    recorder = Recorder()

    def on_press():
        _beep(config.BEEP_FREQ_START)
        recorder.start()

    def on_release():
        audio = recorder.stop()
        _beep(config.BEEP_FREQ_STOP)
        if audio.size == 0:
            raise RuntimeError("No audio data received")
        threading.Thread(target=pipeline, args=(audio,), daemon=True).start()

    def pipeline(audio: np.ndarray):
        raw = transcriber.transcribe(audio)
        if not raw.strip():
            raise RuntimeError("No audio data received")
        print(f"Raw: {raw}")
        cleaned = rewriter.rewrite(raw)
        print(f"Cleaned: {cleaned}")
        processed = post_process(cleaned)
        print(f"Processed: {processed}")
        injector.paste(processed)
        _beep(config.BEEP_FREQ_DONE)

    listener = HotkeyListener(on_press, on_release)
    listener.start()
    listener.join()


if __name__ == "__main__":
    main()
