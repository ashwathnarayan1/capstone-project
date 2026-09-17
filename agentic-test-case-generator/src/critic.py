import re

REQUIRED_CATEGORIES = {"Positive", "Negative", "Boundary", "Edge"}

def covered_acs(test_cases):
    found = set()
    for case in test_cases:
        for ac in re.findall(r"AC\d+", case["Acceptance Criterion"]):
            found.add(ac)
    return found

def category_set(test_cases):
    return {case["Category"] for case in test_cases}

def critique(acceptance_criteria, test_cases):
    expected = set(acceptance_criteria.keys())
    covered = covered_acs(test_cases)
    categories = category_set(test_cases)
    missing = sorted(expected - covered, key=lambda x: int(x[2:]))
    category_gaps = sorted(REQUIRED_CATEGORIES - categories)
    fully_covered = sorted(expected & covered, key=lambda x: int(x[2:]))
    return {
        "covered": fully_covered,
        "partially_covered": [],
        "missing": missing,
        "category_gaps": category_gaps,
        "status": "PASS" if not missing and not category_gaps else "GAPS_FOUND",
        "recommended_test_cases": []
    }
