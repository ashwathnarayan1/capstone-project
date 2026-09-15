# Agentic AI Test Case Generator

This repository contains a capstone assignment solution for generating categorized, requirement-traceable QA test suites from feature specifications.

## What the Agent Does

The agent reads a feature specification and produces:

- Positive, negative, boundary, and edge test cases
- Traceability to acceptance criteria
- Risk-based priority tags
- CSV output suitable for TestRail or Zephyr import
- Gherkin `.feature` files
- A coverage gap report

## Agentic Loop

The solution is intentionally not a single-shot generation. It follows this loop:

```text
Requirement spec
  -> Draft test generation
  -> Coverage critique against acceptance criteria
  -> Gap filling
  -> Final critique
  -> CSV, Gherkin, and coverage report export
```

## Two Modes

### 1. Deterministic demo mode

This mode needs no API key and reliably generates the two assignment suites.

```bash
python src/main.py
```

### 2. LLM mode for future inputs

This mode supports new feature specifications using an OpenAI-compatible or Azure OpenAI chat model.

OpenAI-compatible example:

```bash
export OPENAI_API_KEY="your_api_key"
export OPENAI_MODEL="gpt-4o-mini"
python src/main.py --use-llm --spec specs/my_new_feature.txt --output-dir output
```

Azure OpenAI example:

```bash
export AZURE_OPENAI_API_KEY="your_api_key"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com"
export AZURE_OPENAI_DEPLOYMENT="your-deployment-name"
python src/main.py --use-llm --provider azure --spec specs/my_new_feature.txt --output-dir output
```

## Run Assigned Specs

```bash
python src/main.py
```

Expected output:

```text
Generated 28 final cases for Feature A: User Login
Final review: PASS
Generated 34 final cases for Feature B: Apply Promo Code
Final review: PASS
Coverage report written to output/coverage_gap_report.md
```

## Run One Spec

```bash
python src/main.py --spec specs/feature_a_user_login.txt --output-dir output
```

## Repository Structure

```text
agentic-test-case-generator/
├── README.md
├── requirements.txt
├── src/
│   ├── main.py
│   ├── agent.py
│   ├── llm_client.py
│   ├── parser.py
│   ├── critic.py
│   ├── exporter.py
│   ├── models.py
│   ├── prompts.py
│   └── prebuilt_cases.py
├── specs/
├── output/
├── docs/
└── demo/
```

## Extending the Agent

For any new requirement file, place it in `specs/` and run with `--use-llm`. The agent will ask the LLM to generate a draft suite, critique it, fill gaps if any, and export final outputs.
