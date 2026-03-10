from pathlib import Path
from pynput.keyboard import Key

MODEL_NAME = "Qwen3.5-2B-Q4_K_M.gguf"
BASE_DIR = Path(__file__).resolve().parent

# ── Hotkey ───────────────────────────────────────────────────────────────────
HOTKEY = Key.f9

# ── Audio ────────────────────────────────────────────────────────────────────
SAMPLE_RATE = 16_000
CHANNELS = 1

# ── Transcriber (faster-whisper) ─────────────────────────────────────────────
WHISPER_MODEL_SIZE = "large-v3-turbo"
WHISPER_DEVICE = "cuda"
WHISPER_COMPUTE_TYPE = "float16"
WHISPER_BEAM_SIZE = 1
WHISPER_LANGUAGE = "en"
WHISPER_VAD_FILTER = True

# ── Rewriter (llama.cpp server) ──────────────────────────────────────────────
LLAMA_SERVER_BIN = str(BASE_DIR.parent / "llama.cpp" / "build" / "bin" / "llama-server")
LLAMA_SERVER_HOST = "127.0.0.1"
LLAMA_SERVER_PORT = 8787
LLM_MODEL_PATH = str(BASE_DIR / "models" / MODEL_NAME)
LLM_N_GPU_LAYERS = 99
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
TERMINAL_WM_NAMES = ("terminal", "konsole", "alacritty", "kitty", "tmux", "tilix")

# ── Feedback beeps ───────────────────────────────────────────────────────────
BEEP_ENABLED = True
BEEP_DURATION_MS = 80
BEEP_FREQ_START = 880    # Hz – "recording started"
BEEP_FREQ_STOP = 440     # Hz – "recording stopped"
BEEP_FREQ_DONE = 1320    # Hz – "text pasted"
