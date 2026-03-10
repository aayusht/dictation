import os
import platform
import sys
from pathlib import Path
from pynput.keyboard import Key


MODEL_NAME = "Qwen3.5-2B-Q4_K_M.gguf"
WHISPER_MODEL_NAME = "ggml-small.en-q5_1.bin" # ggml-large-v3-turbo-q5_0.bin
BASE_DIR = Path(__file__).resolve().parent

IS_WINDOWS = sys.platform == "win32"
IS_WINDOWS_ARM = IS_WINDOWS and platform.machine() == "ARM64"
USE_WHISPER_CPP = IS_WINDOWS_ARM

HAS_CUDA = False
if not USE_WHISPER_CPP:
    try:
        import ctranslate2
        HAS_CUDA = "cuda" in ctranslate2.get_supported_compute_types("cuda")
    except Exception:
        pass

# ── Hotkey ───────────────────────────────────────────────────────────────────
HOTKEY = Key.f9

# ── Audio ────────────────────────────────────────────────────────────────────
SAMPLE_RATE = 16_000
CHANNELS = 1

# ── Transcriber ──────────────────────────────────────────────────────────────
WHISPER_LANGUAGE = "en"

if USE_WHISPER_CPP:
    WHISPER_CPP_MODEL_PATH = str(BASE_DIR / "models" / WHISPER_MODEL_NAME)
    if IS_WINDOWS:
        WHISPER_CPP_BIN = str(
            BASE_DIR.parent / "whisper.cpp" / "build" / "bin" / "whisper-server.exe"
        )
    else:
        WHISPER_CPP_BIN = str(
            BASE_DIR.parent / "whisper.cpp" / "build" / "bin" / "whisper-server"
        )
    WHISPER_CPP_HOST = "127.0.0.1"
    WHISPER_CPP_PORT = 8786
    WHISPER_CPP_NO_GPU = True
    WHISPER_CPP_THREADS = max(1, (os.cpu_count() or 4) - 2)
else:
    WHISPER_MODEL_SIZE = "large-v3-turbo"
    WHISPER_DEVICE = "cuda" if HAS_CUDA else "cpu"
    WHISPER_COMPUTE_TYPE = "float16" if HAS_CUDA else "int8"
    WHISPER_BEAM_SIZE = 1
    WHISPER_VAD_FILTER = True

# ── Rewriter (llama.cpp server) ──────────────────────────────────────────────
if IS_WINDOWS:
    LLAMA_SERVER_BIN = str(
        BASE_DIR.parent / "llama.cpp" / "build" / "bin" / "Release" / "llama-server.exe"
    )
else:
    LLAMA_SERVER_BIN = str(
        BASE_DIR.parent / "llama.cpp" / "build" / "bin" / "llama-server"
    )
LLAMA_SERVER_HOST = "127.0.0.1"
LLAMA_SERVER_PORT = 8787
LLM_MODEL_PATH = str(BASE_DIR / "models" / MODEL_NAME)
LLM_N_GPU_LAYERS = 99 if HAS_CUDA else 0
LLM_N_CTX = 2048
LLM_MAX_TOKENS = 512
LLM_TEMPERATURE = 0.0
SKIP_REWRITE = False

# ── Prompts ──────────────────────────────────────────────────────────────────
PROMPTS_DIR = BASE_DIR / "prompts"
DEFAULT_PROMPT_FILE = PROMPTS_DIR / "default.md"
ACTIVE_PROMPT_FILE = DEFAULT_PROMPT_FILE

# ── Injector ─────────────────────────────────────────────────────────────────
# Terminal window-name substrings that trigger Ctrl+Shift+V instead of Ctrl+V
TERMINAL_WM_NAMES = (
    "terminal", "konsole", "alacritty", "kitty", "tmux", "tilix",
    "windows terminal", "powershell", "cmd.exe",
)

# ── Feedback beeps ───────────────────────────────────────────────────────────
BEEP_ENABLED = True
BEEP_DURATION_MS = 80
BEEP_FREQ_START = 880    # Hz – "recording started"
BEEP_FREQ_STOP = 440     # Hz – "recording stopped"
BEEP_FREQ_DONE = 1320    # Hz – "text pasted"
