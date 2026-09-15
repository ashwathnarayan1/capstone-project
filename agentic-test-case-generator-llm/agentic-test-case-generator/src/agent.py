from parser import detect_feature, extract_acceptance_criteria
from prebuilt_cases import LOGIN_CASES, PROMO_CASES
from critic import critique
from prompts import (
    GENERATOR_SYSTEM_PROMPT,
    CRITIC_SYSTEM_PROMPT,
    GAP_FILLER_SYSTEM_PROMPT,
    build_generator_prompt,
    build_critic_prompt,
    build_gap_filler_prompt,
)
from llm_client import LLMClient


class TestCaseGeneratorAgent:
    """Agentic generate-then-critique implementation.

    Modes:
    - Deterministic mode: reliable offline demo for the two supplied capstone specs.
    - LLM mode: generic input support through an OpenAI-compatible or Azure OpenAI chat model.
    """

    def __init__(self, use_llm: bool = False, provider: str = "openai", model: str = None):
        self.use_llm = use_llm
        self.llm_client = LLMClient(provider=provider, model=model) if use_llm else None

    def generate_test_cases(self, spec_text):
        feature = detect_feature(spec_text)
        if not self.use_llm:
            if feature == "login":
                return list(LOGIN_CASES)
            if feature == "promo":
                return list(PROMO_CASES)
            raise ValueError("Unsupported feature spec in deterministic mode. Re-run with --use-llm for generic input support.")

        feature_hint = self._feature_hint(feature)
        prompt = build_generator_prompt(spec_text, feature_hint=feature_hint)
        cases = self.llm_client.generate_json(GENERATOR_SYSTEM_PROMPT, prompt)
        return self._normalize_cases(cases)

    def critique_test_cases(self, spec_text, test_cases):
        if self.use_llm:
            prompt = build_critic_prompt(spec_text, test_cases)
            review = self.llm_client.generate_json(CRITIC_SYSTEM_PROMPT, prompt)
            # Add a deterministic safety check so AC/category gaps are not missed.
            deterministic_review = critique(extract_acceptance_criteria(spec_text), test_cases)
            merged_missing = sorted(set(review.get("missing", [])) | set(deterministic_review.get("missing", [])))
            merged_category_gaps = sorted(set(review.get("category_gaps", [])) | set(deterministic_review.get("category_gaps", [])))
            review["missing"] = merged_missing
            review["category_gaps"] = merged_category_gaps
            review["status"] = "PASS" if not merged_missing and not merged_category_gaps else "GAPS_FOUND"
            return review
        acs = extract_acceptance_criteria(spec_text)
        return critique(acs, test_cases)

    def fill_gaps(self, spec_text, review, existing_count=0):
        if review["status"] == "PASS":
            return []
        if not self.use_llm:
            raise NotImplementedError("Gap templates are not defined for unsupported deterministic specs.")
        feature = detect_feature(spec_text)
        prompt = build_gap_filler_prompt(spec_text, review, existing_count, feature_hint=self._feature_hint(feature))
        cases = self.llm_client.generate_json(GAP_FILLER_SYSTEM_PROMPT, prompt)
        return self._normalize_cases(cases)

    def run(self, spec_text):
        draft_cases = self.generate_test_cases(spec_text)
        first_review = self.critique_test_cases(spec_text, draft_cases)
        added_cases = self.fill_gaps(spec_text, first_review, existing_count=len(draft_cases))
        final_cases = draft_cases + added_cases
        final_review = self.critique_test_cases(spec_text, final_cases)
        return {
            "draft_cases": draft_cases,
            "first_review": first_review,
            "missing_cases_added": added_cases,
            "final_cases": final_cases,
            "final_review": final_review,
        }

    def _feature_hint(self, feature):
        if feature == "login":
            return "LOGIN"
        if feature == "promo":
            return "PROMO"
        return "GEN"

    def _normalize_cases(self, cases):
        if isinstance(cases, dict) and "test_cases" in cases:
            cases = cases["test_cases"]
        if not isinstance(cases, list):
            raise ValueError("LLM response must be a JSON array of test cases.")
        required = ["Test Case ID", "Feature", "Acceptance Criterion", "Category", "Priority", "Risk", "Title", "Preconditions", "Steps", "Test Data", "Expected Result"]
        normalized = []
        for i, case in enumerate(cases, start=1):
            if not isinstance(case, dict):
                continue
            row = {}
            for key in required:
                value = case.get(key, "")
                if isinstance(value, list):
                    value = "; ".join(str(v) for v in value)
                row[key] = str(value)
            if not row["Test Case ID"]:
                row["Test Case ID"] = f"GEN_TC_{i:03d}"
            normalized.append(row)
        return normalized
