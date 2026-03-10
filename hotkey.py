from collections.abc import Callable

from pynput.keyboard import Key, Listener

import config


class HotkeyListener:
    def __init__(self, on_press: Callable[[], None], on_release: Callable[[], None]):
        self._hotkey: Key = config.HOTKEY
        self._on_press = on_press
        self._on_release = on_release
        self._held = False
        self._listener: Listener | None = None

    def _handle_press(self, key: Key) -> None:
        if key == self._hotkey and not self._held:
            self._held = True
            self._on_press()

    def _handle_release(self, key: Key) -> None:
        if key == self._hotkey and self._held:
            self._held = False
            self._on_release()

    def start(self) -> None:
        self._listener = Listener(on_press=self._handle_press, on_release=self._handle_release)
        self._listener.start()

    def stop(self) -> None:
        if self._listener is not None:
            self._listener.stop()
            self._listener = None

    def join(self) -> None:
        if self._listener is not None:
            self._listener.join()
