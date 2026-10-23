"""Guard the proposal's comparison rules and the public-document scan boundary."""

import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check_project", ROOT / "scripts/check_project.py")
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)


class ProjectChecksTests(unittest.TestCase):
    def setUp(self):
        self.plan = json.loads((ROOT / "configs/experiment_plan.json").read_text())

    def test_proposed_protocol_passes(self):
        self.assertEqual(checks.validate_plan(self.plan), [])

    def test_rejects_changed_comparison_and_reporting_rules(self):
        changes = [
            (("threshold", "source"), "test"),
            (("threshold", "auxiliary_fixed_threshold"), 0.6),
            (("evaluation", "comparisons", "primary"), "B-A"),
            (("evaluation", "reporting", "combine_seeds"), "average_probabilities"),
            (("evaluation", "visualization", "seed"), 42),
            (("evaluation", "visualization", "selection_reference_arm"), "A"),
            (("evaluation", "visualization", "probability_ensemble"), True),
        ]
        for path, value in changes:
            with self.subTest(path=path):
                plan = copy.deepcopy(self.plan)
                target = plan
                for key in path[:-1]:
                    target = target[key]
                target[path[-1]] = value
                self.assertTrue(checks.validate_plan(plan))

    def test_public_links_checked_without_traversing_private_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for folder in ("docs", ".github", "data", "reports", "v1", "reports/private"):
                (root / folder).mkdir(parents=True, exist_ok=True)
            (root / "README.md").write_text("[Guide](docs/guide.md)\n")
            (root / "docs/guide.md").write_text("[Missing](missing.md)\n")
            (root / ".github/guide.md").write_text("[Missing](missing.md)\n")
            for name in ("v1/private.md", "reports/private/notes.md", "data/cases.md"):
                (root / name).write_text("[Local artifact](absent.pdf)\n")
            (root / "reports/README.md").write_text("[Missing](missing.md)\n")
            (root / "data/README.md").write_text("[Missing](missing.md)\n")
            errors = checks.check_markdown_links(root)
            self.assertEqual(len(errors), 4)
            self.assertTrue(any("docs/guide.md" in error for error in errors))
            self.assertTrue(any(".github/guide.md" in error for error in errors))
            self.assertTrue(any("reports/README.md" in error for error in errors))
            self.assertTrue(any("data/README.md" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
