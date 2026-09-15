# Design Writeup: Agentic Test Case Generator

## 1. Problem Statement

The goal of this project is to build an AI-assisted QA agent that reads feature specifications and generates requirement-traceable test cases. The test cases must be categorized as positive, negative, boundary, and edge cases, and each test case must map back to one or more acceptance criteria.

## 2. Why an Agentic Approach Was Used

A single generation pass can miss requirements, duplicate test cases, or underrepresent boundary and edge scenarios. To avoid that, this design uses a generate-then-critique loop. The generator creates a draft suite, the critic checks acceptance criterion coverage and category coverage, and the gap filler adds missing test cases before final export.

## 3. Architecture

The solution has five main components:

1. Requirement parser: reads the feature spec and extracts acceptance criteria.
2. Test generator: creates the first draft of test cases.
3. Coverage critic: compares generated test cases against ACs and required categories.
4. Gap filler: adds missing tests if the critic finds coverage gaps.
5. Exporter: writes CSV, Gherkin, and coverage report outputs.

## 4. Prompt and Tool Design

The included implementation is deterministic for reliable demo execution. It also includes prompt placeholders that show how an LLM-based version would be structured:

- Generator prompt: asks the model to act as a senior QA engineer.
- Critic prompt: asks the model to act as a QA coverage reviewer.
- Gap-filler prompt: asks the model to add only missing tests.

Separating these roles improves quality because creation and evaluation are treated as different tasks.

## 5. Output Formats

The agent produces three output types:

- CSV files suitable for TestRail or Zephyr import.
- Gherkin `.feature` files for BDD review.
- Markdown coverage gap report showing AC coverage and category gaps.

## 6. What Broke and How It Was Fixed

### Issue 1: Missing acceptance criteria coverage

Early one-shot test generation tended to cover happy paths first and missed some edge scenarios. This was fixed by adding a critic stage that explicitly checks every `ACn` reference in the generated suite.

### Issue 2: Weak boundary coverage

Boundary points such as five failed login attempts, the 15-minute failure window, 30-minute lockout, 24-hour session expiry, ₹1000 minimum order value, and discount caps can be missed without explicit checking. The test suite now includes these thresholds as separate scenarios.

### Issue 3: Inconsistent output structure

The initial manually drafted format was hard to import into test management tools. This was fixed by using a consistent CSV schema with test case ID, feature, acceptance criterion, category, priority, risk, title, preconditions, steps, test data, and expected result.

### Issue 4: Demo reliability

External LLM/API calls can fail during a live demo. For this capstone, the default implementation uses deterministic local generation for the supplied specs, while preserving agentic architecture and extension points for an LLM-backed generator.

## 7. Final Outcome

The final solution generates 28 test cases for User Login and 34 test cases for Apply Promo Code at Checkout. The coverage report shows all acceptance criteria covered and no category gaps remaining.
