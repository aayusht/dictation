# Dictation Tool

A hands-free dictation system that transcribes your speech, optionally rewrites it using a local LLM (for grammar, formatting, or coding style), and automatically pastes it into your active window. I promise I can actually code but I may have mostly vibe coded this one.

## Features

- **Global Hotkey**: Press and hold `F9` (configurable) to record.
- **Local Transcription**: Uses `faster-whisper` (or `whisper.cpp` on Windows ARM64) for fast, accurate, and private speech-to-text.
- **Local Rewriting**: Uses a local `llama.cpp` server to clean up transcriptions or format them according to specific prompts (e.g., for code or email).
- **Smart Injection**: Automatically pastes text into your active window. It detects terminal windows to use `Ctrl+Shift+V` instead of `Ctrl+V`.
- **Audio Feedback**: Beeps to signal when recording starts, stops, and when the processed text has been pasted.

## Prerequisites

- **Python 3.10+**

### Linux (X11)

- **System Dependencies**:
  - `xclip` (for clipboard management)
  - `xdotool` (for simulating key presses)
  - `libportaudio2` (for audio recording)
  ```bash
  sudo apt-get install xclip xdotool libportaudio2
  ```
- **llama.cpp**:
  ```bash
  git clone https://github.com/ggml-org/llama.cpp && cd llama.cpp
  # With CUDA (NVIDIA GPU):
  cmake -B build -DGGML_CUDA=ON && cmake --build build --config Release -j
  # CPU-only:
  cmake -B build && cmake --build build --config Release -j
  # Then add build/bin to your PATH, or set LLAMA_SERVER_BIN in config.py.
  ```

### Windows 11 (x64)

No system-level dependencies are required — `sounddevice` bundles PortAudio, and clipboard/key simulation use built-in Win32 APIs via `pyperclip` and `pynput`.

- **llama.cpp**:
  Install [CMake](https://cmake.org/download/) and a C++ toolchain (Visual Studio Build Tools or the full IDE). Then:
  ```powershell
  git clone https://github.com/ggml-org/llama.cpp; cd llama.cpp
  cmake -B build                          # CPU-only (no -DGGML_CUDA=ON)
  cmake --build build --config Release -j
  # The binary lands at build\bin\Release\llama-server.exe
  # config.py already points there by default on Windows.
  ```
  If you have an NVIDIA GPU and the CUDA toolkit installed, add `-DGGML_CUDA=ON` to the first `cmake` command.

### Windows 11 (ARM64)

On ARM64 Windows, `faster-whisper` has no native wheels, so the tool uses `whisper.cpp` for transcription instead. Use native ARM64 Python (not x64 emulated) for best performance.

- **llama.cpp** and **whisper.cpp**:
  Install [CMake](https://cmake.org/download/) and a C++ toolchain (Visual Studio Build Tools or the full IDE). Then build both from the parent directory of this repo:
  ```powershell
  # llama.cpp
  git clone https://github.com/ggml-org/llama.cpp; cd llama.cpp
  cmake -B build && cmake --build build --config Release -j
  cd ..

  # whisper.cpp
  git clone https://github.com/ggerganov/whisper.cpp; cd whisper.cpp
  cmake -B build && cmake --build build --config Release -j
  cd ..
  ```
- **Whisper model**: Download a GGML whisper model (e.g. [large-v3-turbo Q5_0](https://huggingface.co/ggerganov/whisper.cpp/blob/main/ggml-large-v3-turbo-q5_0.bin)) and place it in the `models/` directory. Update `WHISPER_CPP_MODEL_PATH` in `config.py` if the filename differs.

### GPU Acceleration (Optional)

A CUDA-compatible NVIDIA GPU speeds up both `faster-whisper` and `llama.cpp`. Without one, everything runs on CPU — just slower. The CUDA-specific Python packages (`nvidia-cublas-cu12`, `nvidia-cudnn-cu12`) are only needed on systems with an NVIDIA GPU; see the installation section for which requirements file to use. On Windows ARM64, GPU acceleration applies to `llama.cpp` and `whisper.cpp` only (not Python-level).

## Installation

1. **Clone the repository**:
  ```bash
   git clone <repository-url>
   cd dictation
  ```
2. **Install Python dependencies**:
  ```bash
   # Linux with NVIDIA GPU:
   pip install -r requirements.txt
   # Windows x64 (or any system without an NVIDIA GPU):
   pip install -r requirements-win.txt
   # Windows ARM64 (uses whisper.cpp instead of faster-whisper):
   pip install -r requirements-win-arm.txt
  ```
3. **Download LLM Model**:
  - Create a `models/` directory.
  - Download a Qwen 3.5 model (e.g. [the 2B quantized model here](https://huggingface.co/unsloth/Qwen3.5-2B-GGUF/blob/main/Qwen3.5-2B-Q4_K_M.gguf)) and place it into the newly created `models/` directory
  - Update `config.py`'s MODEL_NAME if the filename differs from the default.

## Configuration

All settings are managed in `config.py`. Key configurations include:

- `HOTKEY`: The key used to trigger recording (default is `Key.f9`).
- `WHISPER_MODEL_SIZE`: The Whisper model to use for faster-whisper (e.g., `large-v3-turbo`).
- `WHISPER_CPP_MODEL_PATH`: Path to the GGML whisper model (ARM64 only).
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
- `transcriber.py`: Speech-to-text via `faster-whisper` or `whisper.cpp` (auto-selected based on platform).
- `rewriter.py`: Manages a `llama-server` subprocess and queries it for text processing.
- `injector.py`: Handles clipboard and simulated key presses for pasting.
- `hotkey.py`: Global keyboard listener.
- `prompts/`: Directory containing Markdown files used as system prompts for the rewriter.

## Windows ARM64 Notes

On ARM64 Windows, the tool automatically uses `whisper.cpp` for transcription (native ARM64 performance) instead of `faster-whisper` (which has no ARM64 wheels and runs poorly under x64 emulation). This is controlled by `USE_WHISPER_CPP` in `config.py`, which is auto-detected.

