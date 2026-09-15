import csv
from pathlib import Path

HEADERS = ["Test Case ID", "Feature", "Acceptance Criterion", "Category", "Priority", "Risk", "Title", "Preconditions", "Steps", "Test Data", "Expected Result"]


def export_csv(test_cases, output_path):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(test_cases)


def export_gherkin(test_cases, output_path):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    feature_name = test_cases[0]["Feature"] if test_cases else "Generated Test Suite"
    lines = [f"Feature: {feature_name}", ""]
    for case in test_cases:
        tags = "@" + case["Test Case ID"] + " @" + case["Category"].lower() + " @" + case["Priority"].lower() + " @" + case["Acceptance Criterion"].replace(", ", " @")
        lines.append(tags)
        lines.append(f"Scenario: {case['Title']}")
        lines.append(f"  Given {case['Preconditions']}")
        for idx, step in enumerate([s.strip() for s in case["Steps"].split(";") if s.strip()]):
            prefix = "When" if idx == 0 else "And"
            clean_step = step[3:].strip() if len(step) > 2 and step[1:3] == ". " else step
            lines.append(f"  {prefix} {clean_step}")
        lines.append(f"  Then {case['Expected Result']}")
        lines.append("")
    Path(output_path).write_text("\n".join(lines), encoding="utf-8")


def export_coverage_report(results_by_feature, output_path):
    lines = ["# Coverage Gap Report", ""]
    for feature, result in results_by_feature.items():
        review = result["final_review"]
        lines.append(f"## {feature}")
        lines.append("")
        lines.append("| Acceptance Criterion | Status | Notes |")
        lines.append("|---|---|---|")
        for ac in review["covered"]:
            lines.append(f"| {ac} | Covered | Traceable test cases exist. |")
        for ac in review["missing"]:
            lines.append(f"| {ac} | Missing | Needs additional test cases. |")
        lines.append("")
        lines.append(f"Category gaps: {', '.join(review['category_gaps']) if review['category_gaps'] else 'None'}")
        lines.append(f"Final status: {review['status']}")
        lines.append("")
    lines.append("## Summary")
    lines.append("")
    if all(r["final_review"]["status"] == "PASS" for r in results_by_feature.values()):
        lines.append("No acceptance criteria or category gaps remain after the generate-then-critique loop.")
    else:
        lines.append("One or more gaps remain. Review the sections above.")
    Path(output_path).write_text("\n".join(lines), encoding="utf-8")
