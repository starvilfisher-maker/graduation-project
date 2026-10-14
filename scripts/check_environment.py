#!/usr/bin/env python3
"""Read-only environment report; never imports TensorFlow or probes a GPU."""

import importlib.metadata
import json
import platform
import sys


def installed_version(distribution: str) -> str | None:
    try:
        return importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        return None


def main() -> None:
    report = {
        "python": platform.python_version(),
        "python_executable": sys.executable,
        "python_meets_minimum_3_10": sys.version_info >= (3, 10),
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "optional_installed_distributions": {
            name: installed_version(name)
            for name in ("tensorflow", "tensorflow-macos", "tensorflow-metal", "keras")
        },
        "tensorflow_import_tested": False,
        "gpu_availability_tested": False,
        "training_compatibility_verified": False,
        "note": (
            "仅检查环境元数据。安装包存在不代表能够导入、使用 GPU 或完成训练；"
            "仓库基础检查不需要 TensorFlow。"
        ),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

