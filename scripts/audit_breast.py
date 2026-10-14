#!/usr/bin/env python3
"""Audit official local BrEaST files without training or creating a split."""

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from breast_unet.data_audit import audit_dataset


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", default="data/raw/BrEaST-v1", help="Directory relative to the project root")
    parser.add_argument("--output-dir", required=True, help="New audit directory relative to the project root; never overwrite")
    parser.add_argument("--decoding-policy", choices=("strict", "breast_v1"), default="strict",
                        help="strict preserves the first-pass audit; breast_v1 uses the documented decoder")
    args = parser.parse_args()
    try:
        summary = audit_dataset(PROJECT_ROOT, PROJECT_ROOT / args.raw_dir, PROJECT_ROOT / args.output_dir,
                                decoding_policy=args.decoding_policy)
    except ImportError:
        parser.exit(2, "Audit dependencies required: numpy, Pillow, openpyxl. Base checks do not install these.\n")
    except (ValueError, FileNotFoundError, FileExistsError) as exc:
        parser.exit(2, f"Audit stopped: {exc}\n")
    print(json.dumps({key: summary[key] for key in (
        "output_directory", "case_count", "classification_counts", "png_role_counts",
        "automatic_status_counts", "case_issue_counts", "automatic_checks_passed",
        "visual_review_status", "training_ready",
    )}, ensure_ascii=False, indent=2))
    return 0 if summary["automatic_checks_passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
