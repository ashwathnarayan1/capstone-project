from dataclasses import dataclass, asdict
from typing import List

@dataclass
class TestCase:
    test_case_id: str
    feature: str
    acceptance_criterion: str
    category: str
    priority: str
    risk: str
    title: str
    preconditions: str
    steps: str
    test_data: str
    expected_result: str

    def to_csv_row(self):
        return {
            "Test Case ID": self.test_case_id,
            "Feature": self.feature,
            "Acceptance Criterion": self.acceptance_criterion,
            "Category": self.category,
            "Priority": self.priority,
            "Risk": self.risk,
            "Title": self.title,
            "Preconditions": self.preconditions,
            "Steps": self.steps,
            "Test Data": self.test_data,
            "Expected Result": self.expected_result,
        }
