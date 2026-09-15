import json

TEST_CASE_SCHEMA = {
    "Test Case ID": "string, unique and stable, such as LOGIN_TC_001 or GEN_TC_001",
    "Feature": "string",
    "Acceptance Criterion": "string, one or more AC IDs such as AC1 or AC1, AC2",
    "Category": "one of Positive, Negative, Boundary, Edge",
    "Priority": "one of P0, P1, P2, P3",
    "Risk": "short risk area",
    "Title": "short test title",
    "Preconditions": "required setup",
    "Steps": "numbered steps separated by semicolons",
    "Test Data": "input data and important values",
    "Expected Result": "clear expected outcome"
}

GENERATOR_SYSTEM_PROMPT = """You are a senior QA engineer and test design specialist.
Generate high-quality, requirement-traceable test cases from product requirements.
Be precise, avoid duplicates, and cover security, validation, business rules, and calculations where relevant.
Return only valid JSON. Do not include Markdown."""

CRITIC_SYSTEM_PROMPT = """You are a strict QA coverage reviewer.
Review generated test cases against acceptance criteria and required test categories.
Return only valid JSON. Do not include Markdown."""

GAP_FILLER_SYSTEM_PROMPT = """You are a senior QA engineer.
Generate only missing test cases needed to close coverage gaps.
Return only valid JSON. Do not include Markdown."""


def build_generator_prompt(feature_spec: str, feature_hint: str = "GEN") -> str:
    return f"""
Given the feature specification below, generate a categorized test suite.

Requirements:
- Cover every acceptance criterion.
- Include Positive, Negative, Boundary, and Edge cases where applicable.
- Each test case must be traceable to one or more acceptance criteria.
- Include risk-based priority: P0, P1, P2, or P3.
- Use concise but executable steps.
- Return only a JSON array.
- Use this exact object schema for every test case:
{json.dumps(TEST_CASE_SCHEMA, indent=2)}

Feature ID hint for test case IDs: {feature_hint}

Feature specification:
{feature_spec}
""".strip()


def build_critic_prompt(feature_spec: str, test_cases) -> str:
    return f"""
Review the generated test cases against the feature specification.

Check:
1. Every acceptance criterion AC1, AC2, etc. is covered.
2. Required categories are present: Positive, Negative, Boundary, Edge.
3. Each test case has clear traceability, priority, risk, steps, data, and expected result.
4. Identify duplicates or weak cases.
5. Recommend additional test cases only for real gaps.

Return this exact JSON shape:
{{
  "covered": ["AC1"],
  "partially_covered": [],
  "missing": [],
  "category_gaps": [],
  "duplicate_or_weak_cases": [],
  "recommended_test_cases": [
    {{
      "Acceptance Criterion": "ACx",
      "Category": "Positive|Negative|Boundary|Edge",
      "Title": "recommended case title",
      "Reason": "why it is needed"
    }}
  ],
  "status": "PASS or GAPS_FOUND"
}}

Feature specification:
{feature_spec}

Generated test cases:
{json.dumps(test_cases, indent=2, ensure_ascii=False)}
""".strip()


def build_gap_filler_prompt(feature_spec: str, coverage_review, existing_count: int, feature_hint: str = "GEN") -> str:
    return f"""
Generate only the missing test cases identified in the coverage review.

Rules:
- Do not repeat existing cases.
- Start numbering after {existing_count}.
- Use test case ID prefix based on this hint: {feature_hint}_TC.
- Return only a JSON array using this exact object schema:
{json.dumps(TEST_CASE_SCHEMA, indent=2)}

Feature specification:
{feature_spec}

Coverage review:
{json.dumps(coverage_review, indent=2, ensure_ascii=False)}
""".strip()
