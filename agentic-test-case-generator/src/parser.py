import re
from pathlib import Path


def read_spec(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def detect_feature(spec_text: str) -> str:
    lower = spec_text.lower()
    if "user login" in lower or "log in" in lower:
        return "login"
    if "promo code" in lower or "checkout" in lower:
        return "promo"
    return "unknown"


def feature_slug(spec_text: str, fallback: str = "generated") -> str:
    first_nonempty = next((line.strip() for line in spec_text.splitlines() if line.strip()), fallback)
    first_nonempty = re.sub(r"^feature\s+spec\s+[a-z]\s*[—-]\s*", "", first_nonempty, flags=re.I)
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", first_nonempty.lower()).strip("_")
    return slug[:50] or fallback


def extract_acceptance_criteria(spec_text: str):
    pattern = r"(AC\d+)\s*[—-]\s*([^\n]+)"
    return {m.group(1): m.group(2).strip() for m in re.finditer(pattern, spec_text)}
