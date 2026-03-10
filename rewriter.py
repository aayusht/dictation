import atexit
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request

import config


class Rewriter:
    def __init__(self):
        self._process = None
        self._prompt_template = config.ACTIVE_PROMPT_FILE.read_text()
        self._base_url = f"http://{config.LLAMA_SERVER_HOST}:{config.LLAMA_SERVER_PORT}"

        if not config.SKIP_REWRITE:
            self._start_server()
            atexit.register(self.close)

    def _start_server(self) -> None:
        cmd = [
            config.LLAMA_SERVER_BIN,
            "--model", config.LLM_MODEL_PATH,
            "--chat-template-kwargs", '{"enable_thinking": false}',
            "--n-gpu-layers", str(config.LLM_N_GPU_LAYERS),
            "--ctx-size", str(config.LLM_N_CTX),
            "--host", config.LLAMA_SERVER_HOST,
            "--port", str(config.LLAMA_SERVER_PORT),
        ]
        kwargs = dict(stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if sys.platform == "win32":
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
        self._process = subprocess.Popen(cmd, **kwargs)
        try:
            self._wait_for_ready()
        except Exception:
            self._process.kill()
            self._process.wait()
            self._process = None
            raise

    def _wait_for_ready(self, timeout: float = 120.0, interval: float = 0.5) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self._process.poll() is not None:
                raise RuntimeError(
                    f"llama-server exited unexpectedly (code {self._process.returncode})"
                )
            try:
                req = urllib.request.Request(f"{self._base_url}/health")
                with urllib.request.urlopen(req, timeout=2) as resp:
                    if resp.status == 200:
                        return
            except (urllib.error.URLError, OSError):
                pass
            time.sleep(interval)
        raise RuntimeError(f"llama-server did not become ready within {timeout}s")

    def rewrite(self, raw_text: str) -> str:
        if config.SKIP_REWRITE:
            return raw_text

        prompt = self._prompt_template.replace("{raw_text}", raw_text)

        payload = json.dumps({
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": config.LLM_MAX_TOKENS,
            "temperature": config.LLM_TEMPERATURE,
        }).encode()

        req = urllib.request.Request(
            f"{self._base_url}/v1/chat/completions",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
        
        print(f"Raw response:\n{json.dumps(data, indent=2)}")

        return data["choices"][0]["message"]["content"].strip()

    def close(self) -> None:
        if self._process and self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait()
        self._process = None
