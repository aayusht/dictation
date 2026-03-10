# Dictation Tool

A hands-free dictation system that transcribes your speech, optionally rewrites it using a local LLM (for grammar, formatting, or coding style), and automatically pastes it into your active window. I promise I can actually code but I may have mostly vibe coded this one.

## Features

- **Global Hotkey**: Press and hold `F9` (configurable) to record.
- **Local Transcription**: Uses `faster-whisper` for fast, accurate, and private speech-to-text.
- **Local Rewriting**: Uses a local `llama.cpp` server to clean up transcriptions or format them according to specific prompts (e.g., for code or email).
- **Smart Injection**: Automatically pastes text into your active window. It detects terminal windows to use `Ctrl+Shift+V` instead of `Ctrl+V`.
- **Audio Feedback**: Beeps to signal when recording starts, stops, and when the processed text has been pasted.

## Prerequisites

- **Python 3.10+**
- **System Dependencies** (Linux/X11):
  - `xclip` (for clipboard management)
  - `xdotool` (for simulating key presses)
  - `libportaudio2` (for audio recording)
  ```bash
  sudo apt-get install xclip xdotool libportaudio2
  ```
- **llama.cpp**: The `llama-server` binary must be on your `PATH` (or set `LLAMA_SERVER_BIN` in `config.py`).
  ```bash
  # Build from source (with CUDA support):
  git clone https://github.com/ggml-org/llama.cpp && cd llama.cpp
  cmake -B build -DGGML_CUDA=ON && cmake --build build --config Release -j
  # Then add build/bin to your PATH, or copy llama-server somewhere on your PATH.
  ```
- **GPU Acceleration** (Optional but recommended):
  - CUDA-compatible GPU for `faster-whisper` and `llama.cpp`.

## Installation

1. **Clone the repository**:
  ```bash
   git clone <repository-url>
   cd dictation
  ```
2. **Install Python dependencies**:
  ```bash
   pip install -r requirements.txt
  ```
3. **Download LLM Model**:
  - Create a `models/` directory.
  - Download a Qwen 3.5 model (e.g. [the 2B quantized model here](https://huggingface.co/unsloth/Qwen3.5-2B-GGUF/blob/main/Qwen3.5-2B-Q4_K_M.gguf)) and place it into the newly created `models/` directory
  - Update `config.py`'s MODEL_NAME if the filename differs from the default.

## Configuration

All settings are managed in `config.py`. Key configurations include:

- `HOTKEY`: The key used to trigger recording (default is `Key.f9`).
- `WHISPER_MODEL_SIZE`: The Whisper model to use (e.g., `large-v3-turbo`).
- `LLM_MODEL_PATH`: Path to your local GGUF rewriter model.
- `ACTIVE_PROMPT_FILE`: Which prompt to use for rewriting (default is `prompts/default.md`).
- `SKIP_REWRITE`: Set to `True` if you only want raw transcription without LLM processing.

## Usage

1. **Run the application**:
  ```bash
   python main.py
  ```
2. **Wait for models to load**: You will see "Models loaded. Press F9 to dictate."
3. **Dictate**:
  - Press and **hold** `F9`.
  - Speak your message.
  - **Release** `F9`.
4. **Result**: The tool will beep when it finishes processing and paste the text into your currently focused window.

## Project Structure

- `main.py`: Entry point and orchestration of the recording/transcription pipeline.
- `config.py`: Central configuration for hotkeys, models, and audio settings.
- `recorder.py`: Handles audio input using `sounddevice`.
- `transcriber.py`: Wraps `faster-whisper` for speech-to-text.
- `rewriter.py`: Manages a `llama-server` subprocess and queries it for text processing.
- `injector.py`: Handles clipboard and simulated key presses for pasting.
- `hotkey.py`: Global keyboard listener.
- `prompts/`: Directory containing Markdown files used as system prompts for the rewriter.

