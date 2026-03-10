import sys
import threading
import time

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
    print("Models loaded. Press F9 to dictate. Press q in this terminal to quit.")

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
        print("Transcribing…")
        raw = transcriber.transcribe(audio)
        print(f"Raw: {raw}")
        if not raw.strip():
            raise RuntimeError("No audio data received")
        cleaned = rewriter.rewrite(raw)
        print(f"Cleaned: {cleaned}")
        processed = post_process(cleaned)
        print(f"Processed: {processed}")
        injector.paste(processed)
        # _beep(config.BEEP_FREQ_DONE)

    def wait_for_terminal_quit() -> None:
        if sys.platform == "win32":
            import msvcrt

            while True:
                if msvcrt.kbhit():
                    key = msvcrt.getwch()
                    if key in ("\x00", "\xe0"):
                        msvcrt.getwch()
                        continue
                    if key.lower() == "q":
                        return
                time.sleep(0.05)

        while True:
            if input().strip().lower() == "q":
                return

    listener = HotkeyListener(on_press, on_release)
    listener.start()
    try:
        wait_for_terminal_quit()
    except KeyboardInterrupt:
        print("\nStopping…")
    finally:
        listener.stop()
        listener.join()


if __name__ == "__main__":
    main()
