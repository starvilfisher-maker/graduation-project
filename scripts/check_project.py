#!/usr/bin/env python3
"""Check the documented proposal and fixed draft protocol, without real data.

This deliberately does not claim that a training pipeline or dataset is ready.
If the scientific protocol is revised, update its validation rules together
with the configuration and documentation before freezing the new version.
"""

import json
import math
import os
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def check_markdown_links(root: Path) -> list[str]:
    """Check simple inline Markdown links; ignore URLs, anchors and code.

    This is an existence check, not a complete Markdown parser or an anchor
    validator. Generated files, environments and downloaded data are skipped.
    """
    errors: list[str] = []
    excluded = {
        ".git", ".venv", "venv", "__pycache__", "node_modules", "data",
        "datasets", "downloads", "outputs", "runs", "checkpoints", "models",
        "artifacts",
    }
    documents: list[Path] = []
    for directory, subdirectories, filenames in os.walk(root):
        subdirectories[:] = [name for name in subdirectories if name not in excluded]
        documents.extend(Path(directory) / name for name in filenames if name.endswith(".md"))
    if (root / "data/README.md").is_file():
        documents.append(root / "data/README.md")

    link_pattern = re.compile(r"\[[^\]\n]*\]\(\s*(<[^>]*>|[^\s)]+)(?:\s+[\"'][^)]*)?\s*\)")
    for document in sorted(documents):
        fence_character = None
        fence_length = 0
        for line_number, line in enumerate(document.read_text(encoding="utf-8").splitlines(), 1):
            fence = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
            if fence:
                marker, remainder = fence.groups()
                if fence_character is None:
                    fence_character, fence_length = marker[0], len(marker)
                elif marker[0] == fence_character and len(marker) >= fence_length and not remainder.strip():
                    fence_character = None
                continue
            if fence_character is not None or line.startswith(("    ", "\t")):
                continue
            # Inline code may contain illustrative link syntax as well.
            prose = re.sub(r"(`+).*?\1", "", line)
            for match in link_pattern.finditer(prose):
                destination = match.group(1).strip("<>")
                if not destination or destination.startswith(("#", "/")):
                    continue
                parsed = urlsplit(destination)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                target = document.parent / unquote(parsed.path)
                if not target.exists():
                    relative = document.relative_to(root)
                    errors.append(f"{relative}:{line_number}: missing local link target: {destination}")
    return errors


def validate_plan(plan: dict) -> list[str]:
    errors: list[str] = []

    def expect(actual, expected, label):
        if actual != expected:
            errors.append(f"{label}: expected {expected!r}; got {actual!r}")

    expect(plan.get("status"), "planning_not_trained", "status")
    expect(
        plan.get("parameter_status"),
        "proposed_pending_protocol_freeze",
        "parameter_status",
    )
    split = plan.get("split", {})
    expect(split.get("seed"), 20261013, "split seed")
    expect(split.get("stratify"), "Classification", "split stratification")
    expect(split.get("shared_across_all_runs"), True, "shared split")
    ratios = split.get("ratios", {})
    expect(ratios, {"train": 0.6, "validation": 0.2, "test": 0.2}, "split ratios")
    try:
        if not math.isclose(sum(ratios.values()), 1.0, abs_tol=1e-12):
            errors.append("split ratios must sum to 1")
    except (TypeError, AttributeError):
        errors.append("split ratios must be a numeric mapping")

    preprocessing = plan.get("preprocessing", {})
    for key, value in {
        "height": 256,
        "width": 256,
        "channels": 1,
        "resize_policy": "direct_resize",
        "mask_interpolation": "nearest",
        "augment_training_only": True,
    }.items():
        expect(preprocessing.get(key), value, f"preprocessing.{key}")

    expect(plan.get("model", {}).get("channels"), [32, 64, 128, 256, 512], "model channels")
    training = plan.get("training", {})
    expect(training.get("seeds"), [17, 42, 2026], "training seeds")
    expect(training.get("batch_size"), 8, "batch size")
    expect(training.get("max_epochs"), 100, "maximum epochs")
    expect(training.get("optimizer"), "Adam", "optimizer")
    expect(training.get("learning_rate"), 0.001, "learning rate")
    expect(
        training.get("early_stopping"),
        {"monitor": "val_soft_dice", "mode": "max", "patience": 15,
         "min_delta": 0.0001, "restore_best_weights": True},
        "early stopping",
    )
    expect(
        training.get("losses"),
        {"bce": {"bce_weight": 1.0, "dice_loss_weight": 0.0},
         "bce_dice": {"bce_weight": 0.5, "dice_loss_weight": 0.5}},
        "loss definitions",
    )
    augmentation = training.get("augmentation", {})
    for key, value in {
        "probability": 0.5,
        "rotation_degrees": [-10.0, 10.0],
        "translation_fraction_x": [-0.05, 0.05],
        "translation_fraction_y": [-0.05, 0.05],
        "joint_image_mask_transform": True,
        "mask_interpolation": "nearest",
    }.items():
        expect(augmentation.get(key), value, f"augmentation.{key}")

    expected_groups = [
        {"id": "A", "loss": "bce", "augmentation": False},
        {"id": "B", "loss": "bce_dice", "augmentation": False},
        {"id": "C", "loss": "bce", "augmentation": True},
        {"id": "D", "loss": "bce_dice", "augmentation": True},
    ]
    expect(plan.get("groups"), expected_groups, "four experimental groups")
    expected_runs = [
        {"id": f"{group}_seed{seed}", "group": group, "seed": seed}
        for group in "ABCD" for seed in (17, 42, 2026)
    ]
    runs = plan.get("runs", [])
    expect(runs, expected_runs, "12 unique group/seed runs")
    if isinstance(runs, list) and all(isinstance(run, dict) for run in runs):
        run_ids = [run.get("id") for run in runs]
        if len(set(run_ids)) != len(run_ids):
            errors.append("run IDs must be unique")

    threshold = plan.get("threshold", {})
    expect(threshold.get("source"), "validation_only", "threshold selection source")
    expect(threshold.get("per_run"), True, "per-run threshold selection")
    expect(threshold.get("candidates"), [i / 100 for i in range(10, 91, 5)], "threshold grid")
    expect(threshold.get("tie_break"), "closest_to_0.5_then_larger", "threshold tie rule")
    expect(threshold.get("freeze_before_test"), True, "threshold freeze")
    evaluation = plan.get("evaluation", {})
    expect(evaluation.get("resolution"), [256, 256], "evaluation resolution")
    expect(evaluation.get("aggregation"), "macro_case", "evaluation aggregation")
    bootstrap = evaluation.get("bootstrap", {})
    expect(bootstrap.get("replicates"), 5000, "bootstrap replicates")
    expect(bootstrap.get("seed"), 20261013, "bootstrap seed")
    expect(bootstrap.get("unit"), "patient", "bootstrap sampling unit")
    expect(bootstrap.get("paired"), True, "paired bootstrap")
    expect(
        bootstrap.get("seed_handling"),
        "mean_per_patient_across_training_seeds_before_resampling",
        "bootstrap seed handling",
    )
    return errors


def main() -> int:
    required = (
        "README.md", "AGENTS.md", "pyproject.toml", "configs/experiment_plan.json",
        "src/breast_unet/__init__.py", "src/breast_unet/metrics.py",
        "tests/test_metrics.py", "scripts/check_environment.py",
        "scripts/setup_codex.sh", ".github/workflows/check.yml", ".gitignore",
    )
    errors = [f"missing required file: {path}" for path in required if not (ROOT / path).is_file()]
    for number in range(1, 7):
        if not list((ROOT / "docs").glob(f"{number:02d}-*.md")):
            errors.append(f"missing document: docs/{number:02d}-*.md")
    try:
        plan = json.loads((ROOT / "configs/experiment_plan.json").read_text(encoding="utf-8"))
        if not isinstance(plan, dict):
            errors.append("experiment_plan.json must contain an object")
        else:
            errors.extend(validate_plan(plan))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"could not load experiment plan: {exc}")

    errors.extend(check_markdown_links(ROOT))

    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS: core files, local Markdown links and proposed protocol are consistent (4 groups × 3 seeds = 12 runs).")
    print("This verifies the project scaffold only; no dataset or trained model has been validated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

