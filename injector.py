import subprocess

import config


def _get_active_window_name() -> str:
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
    subprocess.run(
        ["xclip", "-selection", "clipboard"],
        input=text, text=True, check=True,
    )
    key = "ctrl+shift+v" if _is_terminal() else "ctrl+v"
    subprocess.run(["xdotool", "key", "--clearmodifiers", key], check=True)
