import json

COLUMNS = ["Test Case ID", "Feature", "Acceptance Criterion", "Category", "Priority", "Risk", "Title", "Preconditions", "Steps", "Test Data", "Expected Result"]

GENERATOR_SYSTEM = """You are a senior QA engineer. Return only one valid JSON object. Keep wording concise. Never return markdown."""
CRITIC_SYSTEM = """You are a strict QA coverage reviewer. Return only one valid JSON object. Never return markdown."""
GAP_SYSTEM = """You are a senior QA engineer closing identified coverage gaps. Return only one valid JSON object. Never return markdown."""


def generator_prompt(spec, prefix):
    return f'''Generate a concise draft test suite for the requirement below.
Return exactly: {{"test_cases": [objects]}}.
Each object must have exactly these keys: {json.dumps(COLUMNS)}.
Rules:
- Maximum 10 draft cases. This is an initial draft, not the final suite.
- Cover every AC at least once.
- Include Positive and Negative cases.
- Include Boundary and Edge only when clearly required.
- Category must be Positive, Negative, Boundary, or Edge.
- Priority must be P0, P1, P2, or P3.
- Steps must be a short semicolon-separated string.
- IDs must start with {prefix}_TC_.
- Keep every field concise to prevent response truncation.

Requirement:
{spec}'''


def critic_prompt(spec, cases):
    slim = [{k: c.get(k, "") for k in ("Test Case ID", "Acceptance Criterion", "Category", "Title", "Expected Result")} for c in cases]
    return f'''Review this draft against the requirement.
Return exactly this JSON object:
{{"covered":[],"partially_covered":[],"missing":[],"category_gaps":[],"recommended_test_cases":[],"status":"PASS or GAPS_FOUND"}}
A category gap exists only when Positive, Negative, Boundary, or Edge is absent from the whole suite.
Recommended test cases must be short objects with Acceptance Criterion, Category, Title, and Reason.

Requirement:
{spec}

Draft summary:
{json.dumps(slim, ensure_ascii=False)}'''


def gap_prompt(spec, review, existing_ids, prefix, start):
    return f'''Generate only cases needed to close this review.
Return exactly: {{"test_cases": [objects]}}.
Use exactly these keys: {json.dumps(COLUMNS)}.
Maximum 8 added cases. Keep all fields concise.
Start IDs at {prefix}_TC_{start:03d}. Do not reuse: {json.dumps(existing_ids)}.
If no real gaps exist, return {{"test_cases":[]}}.

Requirement:
{spec}

Review:
{json.dumps(review, ensure_ascii=False)}'''
