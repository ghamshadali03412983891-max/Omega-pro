
import json
import math
import os
import sys
import argparse
import tempfile
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
SOLVER_DIR = ROOT / "solvers"

if str(SOLVER_DIR) not in sys.path:
    sys.path.insert(0, str(SOLVER_DIR))

from engineering_solver import solve

SUPPORTED_TASKS = [
    "beam",
    "concrete",
    "axial_stress",
    "torque",
    "electrical",
]

def clean_value(value):
    """Convert solver output into safe JSON-compatible values."""
    if hasattr(value, "item"):
        try:
            value = value.item()
        except Exception:
            pass

    if isinstance(value, dict):
        return {str(k): clean_value(v) for k, v in value.items()}

    if isinstance(value, (list, tuple)):
        return [clean_value(v) for v in value]

    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Non-finite numerical result")
        return value

    if isinstance(value, (str, int, bool)) or value is None:
        return value

    return str(value)


def execute_task(task):
    """Execute one engineering task and return a standard response."""

    task_id = None

    try:
        if not isinstance(task, dict):
            raise ValueError("Task must be a JSON object")

        task_id = task.get("id")
        name = task.get("task")

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Missing task name")

        name = name.strip().lower()

        if name not in SUPPORTED_TASKS:
            raise ValueError(
                "Unsupported task: " + name +
                ". Supported tasks: " + ", ".join(SUPPORTED_TASKS)
            )

        parameters = task.get("parameters", task.get("params"))

        if not isinstance(parameters, dict):
            raise ValueError("Task requires a parameters object")

        result = solve(name, **parameters)
        result = clean_value(result)

        return {
            "id": task_id,
            "task": name,
            "status": "SUCCESS",
            "result": result,
            "timestamp_utc": datetime.now(timezone.utc).isoformat()
        }

    except Exception as exc:
        return {
            "id": task_id,
            "task": task.get("task") if isinstance(task, dict) else None,
            "status": "ERROR",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "timestamp_utc": datetime.now(timezone.utc).isoformat()
        }


def atomic_json_write(path, data):
    """Write JSON safely without leaving a half-written output file."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fd, temp_name = tempfile.mkstemp(
        prefix=path.name,
        suffix=".tmp",
        dir=str(path.parent)
    )

    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())

        os.replace(temp_name, path)

    except Exception:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise


def run_input_file(input_path, output_path=None):
    """Run a single task or a list of tasks from a JSON file."""

    input_path = Path(input_path)

    if not input_path.exists():
        raise FileNotFoundError(str(input_path))

    with input_path.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    if isinstance(payload, list):
        results = [execute_task(item) for item in payload]
    else:
        results = execute_task(payload)

    if output_path is not None:
        atomic_json_write(output_path, results)

    return results


def run_inbox(inbox_dir, output_dir):
    """Process JSON task files placed in the inbox directory."""

    inbox_dir = Path(inbox_dir)
    output_dir = Path(output_dir)

    inbox_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    processed = []

    for input_file in sorted(inbox_dir.glob("*.json")):
        output_file = output_dir / (input_file.stem + "_result.json")

        try:
            result = run_input_file(input_file, output_file)
            processed.append({
                "input": input_file.name,
                "output": output_file.name,
                "status": "PROCESSED"
            })
        except Exception as exc:
            error_result = {
                "status": "ERROR",
                "input": input_file.name,
                "error": str(exc)
            }
            atomic_json_write(output_file, error_result)

            processed.append({
                "input": input_file.name,
                "output": output_file.name,
                "status": "ERROR",
                "error": str(exc)
            })

    return processed


def main():
    parser = argparse.ArgumentParser(
        description="Offline Engineering Task Agent"
    )

    parser.add_argument("--input", help="Input JSON task file")
    parser.add_argument("--output", help="Output JSON result file")
    parser.add_argument("--inbox", help="Directory containing task JSON files")
    parser.add_argument("--outdir", help="Directory for inbox results")

    args = parser.parse_args()

    if args.input:
        result = run_input_file(args.input, args.output)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.inbox:
        results = run_inbox(
            args.inbox,
            args.outdir or str(Path(args.inbox).parent / "outputs")
        )
        print(json.dumps(results, indent=2, ensure_ascii=False))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
