import csv
import json
from pathlib import Path

HEADERS = ["Test Case ID", "Feature", "Acceptance Criterion", "Category", "Priority", "Risk", "Title", "Preconditions", "Steps", "Test Data", "Expected Result"]


def export_json(data, path):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def export_csv(rows, path):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=HEADERS); writer.writeheader(); writer.writerows(rows)


def export_gherkin(rows, path):
    feature = rows[0]["Feature"] if rows else "Generated Feature"
    lines = [f"Feature: {feature}", ""]
    for row in rows:
        lines += [f"@{row['Test Case ID']} @{row['Category'].lower()} @{row['Priority'].lower()}", f"Scenario: {row['Title']}", f"  Given {row['Preconditions']}"]
        for i, step in enumerate([s.strip() for s in row["Steps"].split(";") if s.strip()]):
            lines.append(f"  {'When' if i == 0 else 'And'} {restrip(step)}")
        lines += [f"  Then {row['Expected Result']}", ""]
    Path(path).write_text("\n".join(lines), encoding="utf-8")


def restrip(step):
    import re
    return re.sub(r"^\d+\.\s*", "", step)
