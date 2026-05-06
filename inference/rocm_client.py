"""
AMD Developer Cloud / vLLM inference client.
Wraps the OpenAI-compatible API exposed by vLLM running on ROCm.
"""
import os
import httpx
from typing import Optional

VLLM_BASE_URL = os.getenv("VLLM_BASE_URL", "http://localhost:8080/v1")
AMD_API_KEY = os.getenv("AMD_CLOUD_API_KEY", "EMPTY")
DEFAULT_MODEL = os.getenv("VLLM_MODEL", "deepseek-ai/DeepSeek-R1-Distill-Llama-70B")


async def chat_completion(
    messages: list[dict],
    model: Optional[str] = None,
    temperature: float = 0.1,
    max_tokens: int = 1024,
) -> str:
    """
    Call the vLLM chat completions endpoint asynchronously.
    Returns the assistant message content string.
    """
    url = f"{VLLM_BASE_URL}/chat/completions"
    payload = {
        "model": model or DEFAULT_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    headers = {"Authorization": f"Bearer {AMD_API_KEY}"}

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


def chat_completion_sync(
    messages: list[dict],
    model: Optional[str] = None,
    temperature: float = 0.1,
    max_tokens: int = 1024,
) -> str:
    """Synchronous wrapper around chat_completion."""
    url = f"{VLLM_BASE_URL}/chat/completions"
    payload = {
        "model": model or DEFAULT_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    headers = {"Authorization": f"Bearer {AMD_API_KEY}"}
    with httpx.Client(timeout=120.0) as client:
        response = client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


def list_models() -> list[str]:
    """List available models on the vLLM server."""
    with httpx.Client(timeout=10.0) as client:
        response = client.get(
            f"{VLLM_BASE_URL}/models",
            headers={"Authorization": f"Bearer {AMD_API_KEY}"},
        )
        response.raise_for_status()
        return [m["id"] for m in response.json().get("data", [])]
