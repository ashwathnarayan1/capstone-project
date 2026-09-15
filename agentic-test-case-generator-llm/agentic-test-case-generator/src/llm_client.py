import json
import os
import re
import urllib.error
import urllib.request
from typing import Any, Dict, List


class LLMClientError(Exception):
    pass


class LLMClient:
    """Small OpenAI-compatible chat client using only Python standard library.

    Environment variables:
    - OPENAI_API_KEY: required for OpenAI-compatible endpoints
    - OPENAI_BASE_URL: optional, default https://api.openai.com/v1
    - OPENAI_MODEL: optional, default gpt-4o-mini

    Azure OpenAI-compatible environment variables:
    - AZURE_OPENAI_API_KEY
    - AZURE_OPENAI_ENDPOINT, for example https://my-resource.openai.azure.com
    - AZURE_OPENAI_DEPLOYMENT
    - AZURE_OPENAI_API_VERSION, default 2024-02-15-preview
    """

    def __init__(self, provider: str = "openai", model: str = None):
        self.provider = provider.lower()
        self.model = model

    def generate_text(self, system_prompt: str, user_prompt: str, temperature: float = 0.1) -> str:
        if self.provider == "azure":
            return self._azure_chat(system_prompt, user_prompt, temperature)
        return self._openai_compatible_chat(system_prompt, user_prompt, temperature)

    def generate_json(self, system_prompt: str, user_prompt: str, temperature: float = 0.1) -> Any:
        text = self.generate_text(system_prompt, user_prompt, temperature)
        return parse_json_from_text(text)

    def _openai_compatible_chat(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise LLMClientError("OPENAI_API_KEY is not set. Set it or run without --use-llm for deterministic demo mode.")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        model = self.model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        url = f"{base_url}/chat/completions"
        payload = {
            "model": model,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        return self._post_chat(url, payload, {"Authorization": f"Bearer {api_key}"})

    def _azure_chat(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
        deployment = self.model or os.getenv("AZURE_OPENAI_DEPLOYMENT")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        if not api_key or not endpoint or not deployment:
            raise LLMClientError("Azure variables missing. Set AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, and AZURE_OPENAI_DEPLOYMENT.")
        url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version={api_version}"
        payload = {
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        return self._post_chat(url, payload, {"api-key": api_key})

    def _post_chat(self, url: str, payload: Dict[str, Any], extra_headers: Dict[str, str]) -> str:
        body = json.dumps(payload).encode("utf-8")
        headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "agentic-test-case-generator/1.0",
    **extra_headers,
}
        request = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise LLMClientError(f"LLM HTTP error {exc.code}: {error_body}") from exc
        except urllib.error.URLError as exc:
            raise LLMClientError(f"LLM connection error: {exc}") from exc
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMClientError(f"Unexpected LLM response: {data}") from exc


def parse_json_from_text(text: str) -> Any:
    """Parse JSON even if the model wraps it in Markdown fences."""
    cleaned = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", cleaned, flags=re.DOTALL | re.IGNORECASE)
    if fence:
        cleaned = fence.group(1).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = min([pos for pos in [cleaned.find("["), cleaned.find("{")] if pos != -1], default=-1)
        end = max(cleaned.rfind("]"), cleaned.rfind("}"))
        if start != -1 and end != -1 and end > start:
            return json.loads(cleaned[start:end + 1])
        raise
