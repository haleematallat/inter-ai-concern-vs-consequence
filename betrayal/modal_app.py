"""Serve one open-weight model with vLLM on Modal, behind an OpenAI-compatible endpoint.

Shape taken from Modal's own vLLM example (https://modal.com/docs/examples/vllm_inference, vLLM 0.21.0).
**Untested: this file has never been deployed.** No Modal credentials were available in the session that
wrote it, so check the decorator names and the vLLM version against Modal's current docs before the first
`modal serve`, and treat the first run as the smoke test.

    modal serve betrayal/modal_app.py                      # ephemeral; prints a URL, stops on Ctrl-C
    export VLLM_BASE_URL=https://<...>.modal.run/v1
    python -m betrayal.cuestate behavior --model Qwen/Qwen3-32B --cells core_distress_stuck_agent

With VLLM_BASE_URL set, betrayal/llm.py routes every call to this server instead of OpenRouter and records
$0 per call, because a self-hosted server is billed in GPU-hours. The OpenRouter cap therefore does **not**
bound a Modal run: `scaledown_window` and the cost table in betrayal/modal_cost.py are what bound it.
"""
import os
import subprocess

import modal

MODEL = os.environ.get("VLLM_MODEL", "Qwen/Qwen3-32B")
N_GPU = int(os.environ.get("VLLM_N_GPU", "1"))
GPU = os.environ.get("VLLM_GPU", "H100")
PORT = 8000

image = (
    modal.Image.from_registry("nvidia/cuda:12.9.0-devel-ubuntu22.04", add_python="3.12")
    .entrypoint([])
    .uv_pip_install("vllm==0.21.0", "huggingface_hub[hf_transfer]")
    .env({"HF_XET_HIGH_PERFORMANCE": "1", "VLLM_LOG_STATS_INTERVAL": "5"})
)
hf_cache = modal.Volume.from_name("huggingface-cache", create_if_missing=True)
vllm_cache = modal.Volume.from_name("vllm-cache", create_if_missing=True)
app = modal.App("cuestate-vllm")


@app.server(
    image=image,
    gpu=f"{GPU}:{N_GPU}",
    volumes={"/root/.cache/huggingface": hf_cache, "/root/.cache/vllm": vllm_cache},
    scaledown_window=5 * 60,     # idle GPU time is the main way a run overspends; keep it short
    startup_timeout=15 * 60,
    port=PORT,
    target_concurrency=64,
    unauthenticated=True,
)
class Server:
    @modal.enter()
    def start(self):
        self.proc = subprocess.Popen([
            "vllm", "serve", MODEL,
            "--host", "0.0.0.0", "--port", str(PORT),
            "--tensor-parallel-size", str(N_GPU),
            "--served-model-name", MODEL,
            "--max-model-len", "4096",       # the longest prompt here is well under 1k tokens
            "--disable-log-requests",        # prompts are the experiment's material; do not ship them to logs
        ])

    @modal.exit()
    def stop(self):
        self.proc.terminate()
        self.proc.wait(timeout=60)
