import sys
import time

import pyperclip
from pynput.keyboard import Controller, Key

import config

_kb = Controller()


def _get_active_window_name() -> str:
    if sys.platform == "win32":
        import ctypes
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        buf = ctypes.create_unicode_buffer(256)
        ctypes.windll.user32.GetWindowTextW(hwnd, buf, 256)
        return buf.value
    else:
        import subprocess
        wid = subprocess.run(
            ["xdotool", "getactivewindow"],
            capture_output=True, text=True,
        ).stdout.strip()
        if not wid:
            return ""
        return subprocess.run(
            ["xdotool", "getwindowname", wid],
            capture_output=True, text=True,
        ).stdout.strip()


def _is_terminal() -> bool:
    name = _get_active_window_name().lower()
    return any(t in name for t in config.TERMINAL_WM_NAMES)


def paste(text: str) -> None:
    pyperclip.copy(text)
    time.sleep(0.05)

    if _is_terminal() and sys.platform != "win32":
        with _kb.pressed(Key.ctrl_l), _kb.pressed(Key.shift):
            _kb.tap("v")
    else:
        with _kb.pressed(Key.ctrl_l):
            _kb.tap("v")
