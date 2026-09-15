# 10-Minute Demo Script

## Minute 1: Problem

I built an agentic test case generator that reads feature specifications and creates categorized, traceable QA test suites.

## Minute 2: Architecture

Show the flow:

```text
Parser -> Generator -> Critic -> Gap Filler -> Exporter
```

Explain that the critic checks acceptance criterion coverage and category coverage.

## Minutes 3 to 5: Run the Agent

```bash
python src/main.py
```

Expected console output:

```text
Generated 28 final cases for Feature A: User Login
Final review: PASS
Generated 34 final cases for Feature B: Apply Promo Code
Final review: PASS
Coverage report written to output/coverage_gap_report.md
```

## Minutes 6 to 7: Show Outputs

Open these files:

```text
output/feature_a_test_cases.csv
output/feature_b_test_cases.csv
output/coverage_gap_report.md
```

Call out these examples:

- Login lockout after five failed attempts within 15 minutes.
- Correct credentials still blocked during 30-minute lockout.
- Promo minimum order boundary at ₹999 and ₹1000.
- Promo discount cap so subtotal never becomes negative.
- Promo revalidation after cart subtotal changes.

## Minutes 8 to 9: Explain Agentic Behavior

The solution is not a single-shot generator. It drafts test cases first, critiques coverage, identifies missing ACs or category gaps, and then provides a final suite.

## Minute 10: Reflection

The agent was most useful for coverage review, boundary cases, edge cases, and standardizing output. Human QA review is still required for business assumptions and test data validation.
