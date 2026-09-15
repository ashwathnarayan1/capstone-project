import argparse
from pathlib import Path
from agent import TestCaseGeneratorAgent
from parser import read_spec, detect_feature, feature_slug
from exporter import export_csv, export_gherkin, export_coverage_report


def output_names(feature_key, spec_text):
    if feature_key == "login":
        return "feature_a_test_cases.csv", "feature_a_login.feature", "Feature A: User Login"
    if feature_key == "promo":
        return "feature_b_test_cases.csv", "feature_b_promo_code.feature", "Feature B: Apply Promo Code"
    slug = feature_slug(spec_text)
    return f"{slug}_test_cases.csv", f"{slug}.feature", f"Generated Feature: {slug}"


def run_one(spec_path, output_dir, use_llm=False, provider="openai", model=None):
    spec_text = read_spec(spec_path)
    feature_key = detect_feature(spec_text)
    csv_name, feature_name, display_name = output_names(feature_key, spec_text)
    agent = TestCaseGeneratorAgent(use_llm=use_llm, provider=provider, model=model)
    result = agent.run(spec_text)
    export_csv(result["final_cases"], Path(output_dir) / csv_name)
    export_gherkin(result["final_cases"], Path(output_dir) / feature_name)
    return display_name, result


def main():
    parser = argparse.ArgumentParser(description="Agentic Test Case Generator")
    parser.add_argument("--spec", action="append", help="Path to a feature spec. Can be supplied multiple times.")
    parser.add_argument("--output-dir", default="output", help="Directory for generated outputs.")
    parser.add_argument("--use-llm", action="store_true", help="Use LLM generator for generic input support.")
    parser.add_argument("--provider", choices=["openai", "azure"], default="openai", help="LLM provider. Default: openai-compatible.")
    parser.add_argument("--model", default=None, help="Model name or Azure deployment name. Optional if set with env vars.")
    args = parser.parse_args()

    specs = args.spec or ["specs/feature_a_user_login.txt", "specs/feature_b_promo_code.txt"]
    results = {}
    for spec in specs:
        display_name, result = run_one(spec, args.output_dir, use_llm=args.use_llm, provider=args.provider, model=args.model)
        results[display_name] = result
        print(f"Generated {len(result['final_cases'])} final cases for {display_name}")
        print(f"First review: {result['first_review']['status']}")
        print(f"Missing cases added: {len(result['missing_cases_added'])}")
        print(f"Final review: {result['final_review']['status']}")
    export_coverage_report(results, Path(args.output_dir) / "coverage_gap_report.md")
    print(f"Coverage report written to {args.output_dir}/coverage_gap_report.md")


if __name__ == "__main__":
    main()
