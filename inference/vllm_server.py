"""
vLLM server launcher for AMD ROCm.
Run this script on the AMD Developer Cloud MI300X instance to start
the inference server before launching the agent mesh.

Usage:
    python inference/vllm_server.py

Requirements:
    pip install vllm  (ROCm build)
    ROCm 6.x installed
"""
import os
import subprocess
import sys

MODEL = os.getenv("VLLM_MODEL", "deepseek-ai/DeepSeek-R1-Distill-Llama-70B")
HOST = "0.0.0.0"
PORT = "8080"
GPU_MEMORY_UTILIZATION = "0.90"
MAX_MODEL_LEN = "32768"
TENSOR_PARALLEL_SIZE = "1"  # Increase for multi-GPU


def main():
    cmd = [
        sys.executable, "-m", "vllm.entrypoints.openai.api_server",
        "--model", MODEL,
        "--host", HOST,
        "--port", PORT,
        "--gpu-memory-utilization", GPU_MEMORY_UTILIZATION,
        "--max-model-len", MAX_MODEL_LEN,
        "--tensor-parallel-size", TENSOR_PARALLEL_SIZE,
        "--dtype", "bfloat16",
        "--trust-remote-code",
    ]
    print(f"Starting vLLM with model: {MODEL}")
    print(f"Server will be at: http://{HOST}:{PORT}/v1")
    print("ROCm device:", os.getenv("ROCR_VISIBLE_DEVICES", "all"))
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
