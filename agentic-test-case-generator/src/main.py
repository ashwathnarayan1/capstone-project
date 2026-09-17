import argparse
import json
import re
from pathlib import Path
from agent import TestCaseGeneratorAgent
from exporter import export_json, export_csv, export_gherkin


def main():
    parser = argparse.ArgumentParser(description="AI Agentic Test Case Generator")
    parser.add_argument("--spec", required=True)
    parser.add_argument("--output-dir", default="ai_output")
    parser.add_argument("--model", default=None)
    args = parser.parse_args()

    spec = Path(args.spec).read_text(encoding="utf-8")
    result = TestCaseGeneratorAgent(args.model).run(spec)
    out = Path(args.output_dir); out.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "_", next((x for x in spec.lower().splitlines() if x.strip()), "feature")).strip("_")[:50]

    export_json(result["draft_cases"], out / "01_draft_test_cases.json")
    export_json(result["first_review"], out / "02_first_ai_critique.json")
    export_json(result["missing_cases_added"], out / "03_missing_test_cases_added.json")
    export_json(result["final_review"], out / "04_final_ai_critique.json")
    export_csv(result["final_cases"], out / f"{slug}_final_test_cases.csv")
    export_gherkin(result["final_cases"], out / f"{slug}_final_test_cases.feature")
    summary = {"model": args.model, "input_spec": args.spec, "draft_count": len(result["draft_cases"]), "first_review": result["first_review"]["status"], "cases_added": len(result["missing_cases_added"]), "final_count": len(result["final_cases"]), "final_review": result["final_review"]["status"]}
    export_json(summary, out / "agent_run_summary.json")
    print("\nAgent completed. Outputs saved to:", out)


if __name__ == "__main__":
    main()
