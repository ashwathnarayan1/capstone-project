import re
from llm_client import LLMClient
from prompts import GENERATOR_SYSTEM, CRITIC_SYSTEM, GAP_SYSTEM, generator_prompt, critic_prompt, gap_prompt

REQUIRED_CATEGORIES = {"Positive", "Negative", "Boundary", "Edge"}
COLUMNS = ["Test Case ID", "Feature", "Acceptance Criterion", "Category", "Priority", "Risk", "Title", "Preconditions", "Steps", "Test Data", "Expected Result"]


class TestCaseGeneratorAgent:
    def __init__(self, model=None):
        self.client = LLMClient(model=model)

    def run(self, spec):
        prefix = self._prefix(spec)
        print("Stage 1: AI is generating draft test cases...")
        draft = self._cases(self.client.generate_json(GENERATOR_SYSTEM, generator_prompt(spec, prefix), 0.15,1800), prefix, 1)
        print("Draft cases generated:", len(draft))

        print("Stage 2: AI critic is reviewing the draft...")
        first = self.client.generate_json(CRITIC_SYSTEM, critic_prompt(spec, draft), 0.05, 900)
        first = self._guardrail(spec, draft, first)
        print("First review status:", first["status"])
        print("Missing ACs:", first["missing"])
        print("Category gaps:", first["category_gaps"])

        print("Stage 3: AI is filling coverage gaps...")
        if first["status"] == "PASS":
            added = []
        else:
            raw = self.client.generate_json(GAP_SYSTEM, gap_prompt(spec, first, [x["Test Case ID"] for x in draft], prefix, len(draft)+1), 0.1,1600)
            added = self._cases(raw, prefix, len(draft)+1)
        print("Missing cases added:", len(added))

        final_cases = draft + added
        print("Stage 4: AI critic is performing final review...")
        final = self.client.generate_json(CRITIC_SYSTEM, critic_prompt(spec, final_cases), 0.05, 900)
        final = self._guardrail(spec, final_cases, final)
        print("Final review status:", final["status"])
        return {"draft_cases": draft, "first_review": first, "missing_cases_added": added, "final_cases": final_cases, "final_review": final}

    def _cases(self, raw, prefix, start):
        if isinstance(raw, dict):
            raw = raw.get("test_cases", raw.get("cases", []))
        if not isinstance(raw, list):
            raise ValueError("AI response did not contain a test_cases array")
        result = []
        for number, item in enumerate(raw, start=start):
            if not isinstance(item, dict):
                continue
            row = {key: self._text(item.get(key, "")) for key in COLUMNS}
            if not row["Test Case ID"]:
                row["Test Case ID"] = f"{prefix}_TC_{number:03d}"
            result.append(row)
        if not result:
            raise ValueError("AI returned no usable test cases")
        return result

    def _guardrail(self, spec, cases, review):
        review = review if isinstance(review, dict) else {}
        expected = set(re.findall(r"\bAC\d+\b", spec, re.I))
        covered = set()
        categories = set()
        for case in cases:
            covered.update(re.findall(r"\bAC\d+\b", case.get("Acceptance Criterion", ""), re.I))
            category = case.get("Category", "").title()
            if category:
                categories.add(category)
        missing = sorted(expected - covered, key=self._ac_number)
        category_gaps = sorted(REQUIRED_CATEGORIES - categories)
        ai_missing = {str(x).upper() for x in review.get("missing", []) if re.fullmatch(r"AC\d+", str(x), re.I)}
        missing = sorted(set(missing) | ai_missing, key=self._ac_number)
        category_gaps = sorted(set(category_gaps) | set(review.get("category_gaps", [])))
        review.setdefault("covered", sorted(expected & covered, key=self._ac_number))
        review.setdefault("partially_covered", [])
        review.setdefault("recommended_test_cases", [])
        review["missing"] = missing
        review["category_gaps"] = category_gaps
        review["status"] = "PASS" if not missing and not category_gaps else "GAPS_FOUND"
        return review

    @staticmethod
    def _text(value):
        if isinstance(value, list):
            return "; ".join(str(v) for v in value)
        return str(value).strip()

    @staticmethod
    def _ac_number(value):
        match = re.search(r"\d+", str(value))
        return int(match.group()) if match else 99999

    @staticmethod
    def _prefix(spec):
        heading = next((x.strip() for x in spec.splitlines() if x.strip()), "GEN")
        words = re.findall(r"[A-Za-z]+", heading)
        return "".join(word[0].upper() for word in words[-3:]) or "GEN"
