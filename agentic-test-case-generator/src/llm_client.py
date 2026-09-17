import json
import os
import re
import time
import urllib.error
import urllib.request


class LLMClientError(Exception):
    pass


class LLMClient:

    def __init__(self, model=None):
        self.model = model or os.getenv("OPENAI_MODEL")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise LLMClientError("OPENAI_API_KEY is not configured")
        if not self.model:
            raise LLMClientError("OPENAI_MODEL is not configured")

    def generate_json(self, system_prompt, user_prompt, temperature=0.1, max_tokens=6000):
        text = self._chat(system_prompt, user_prompt, temperature, max_tokens)
        try:
            return parse_json(text)
        except Exception:
            repair_system = "You repair malformed JSON. Return only valid JSON with no markdown. Preserve all complete information."
            repair_user = "Repair the following malformed JSON response. If the ending is truncated, close the current object and array correctly.\n\n" + text
            repaired = self._chat(repair_system, repair_user, 0.0, max_tokens)
            return parse_json(repaired)

    def _chat(
        self,
        system_prompt,
        user_prompt,
        temperature,
        max_tokens
    ):
        url = f"{self.base_url}/chat/completions"
 
        payload = {
            "model": self.model,
            "temperature": temperature,
            "max_completion_tokens": max_tokens,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        }
 
        body = json.dumps(payload).encode("utf-8")
 
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": (
                "agentic-test-case-generator/2.0"
            )
        }
 
        maximum_attempts = 5
 
        for attempt in range(
            1,
            maximum_attempts + 1
        ):
            request = urllib.request.Request(
                url,
                data=body,
                headers=headers,
                method="POST"
            )
 
            try:
                with urllib.request.urlopen(
                    request,
                    timeout=180
                ) as response:
                    response_body = (
                        response.read().decode(
                            "utf-8"
                        )
                    )
 
                    data = json.loads(
                        response_body
                    )
 
                    return data[
                        "choices"
                    ][0]["message"]["content"]
 
            except urllib.error.HTTPError as exc:
                error_body = exc.read().decode(
                    "utf-8",
                    errors="replace"
                )
 
                if exc.code == 429:
                    wait_seconds = 65.0
 
                    retry_after = (
                        exc.headers.get(
                            "Retry-After"
                        )
                        if exc.headers
                        else None
                    )
 
                    if retry_after:
                        try:
                            wait_seconds = (
                                float(retry_after)
                                + 3
                            )
                        except ValueError:
                            pass
 
                    retry_match = re.search(
                        r"try again in "
                        r"([0-9]+(?:\.[0-9]+)?)s",
                        error_body,
                        flags=re.IGNORECASE
                    )
 
                    if retry_match:
                        wait_seconds = max(
                            float(
                                retry_match.group(1)
                            ) + 3,
                            20.0
                        )
 
                    if attempt < maximum_attempts:
                        print(
                            "API rate limit reached. "
                            f"Waiting "
                            f"{wait_seconds:.0f} "
                            "seconds before retrying..."
                        )
 
                        time.sleep(wait_seconds)
 
                        continue
 
                raise LLMClientError(
                    f"LLM HTTP {exc.code}: "
                    f"{error_body}"
                ) from exc
 
            except urllib.error.URLError as exc:
                if attempt < maximum_attempts:
                    wait_seconds = attempt * 5
 
                    print(
                        "Temporary connection "
                        "error. "
                        f"Retrying in "
                        f"{wait_seconds} seconds..."
                    )
 
                    time.sleep(wait_seconds)
 
                    continue
 
                raise LLMClientError(
                    "LLM connection error: "
                    f"{exc}"
                ) from exc
 
            except (
                KeyError,
                IndexError,
                TypeError
            ) as exc:
                raise LLMClientError(
                    "Unexpected LLM response: "
                    f"{data}"
                ) from exc
 
        raise LLMClientError(
            "LLM request failed after "
            f"{maximum_attempts} attempts."
        )    

    # def _chat(self, system_prompt, user_prompt, temperature, max_tokens):
    #     url = f"{self.base_url}/chat/completions"
    #     payload = {
    #         "model": self.model,
    #         "temperature": temperature,
    #         "max_completion_tokens": max_tokens,
    #         "messages": [
    #             {"role": "system", "content": system_prompt},
    #             {"role": "user", "content": user_prompt},
    #         ],
    #     }
    #     body = json.dumps(payload).encode("utf-8")
    #     headers = {
    #         "Authorization": f"Bearer {self.api_key}",
    #         "Content-Type": "application/json",
    #         "Accept": "application/json",
    #         "User-Agent": "agentic-test-case-generator/2.0",
    #     }
    #     request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    #     try:
    #         with urllib.request.urlopen(request, timeout=180) as response:
    #             data = json.loads(response.read().decode("utf-8"))
    #     except urllib.error.HTTPError as exc:
    #         detail = exc.read().decode("utf-8", errors="replace")
    #         raise LLMClientError(f"LLM HTTP {exc.code}: {detail}") from exc
    #     except urllib.error.URLError as exc:
    #         raise LLMClientError(f"LLM connection error: {exc}") from exc
    #     try:
    #         return data["choices"][0]["message"]["content"]
    #     except (KeyError, IndexError, TypeError) as exc:
    #         raise LLMClientError(f"Unexpected LLM response: {data}") from exc


def parse_json(text):
    cleaned = text.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)```", cleaned, re.I | re.S)
    if fenced:
        cleaned = fenced.group(1).strip()
    decoder = json.JSONDecoder()
    for marker in ("{", "["):
        start = cleaned.find(marker)
        if start >= 0:
            try:
                value, _ = decoder.raw_decode(cleaned[start:])
                return value
            except json.JSONDecodeError:
                pass
    return json.loads(cleaned)
