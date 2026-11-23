
import json
from pathlib import Path
from engineering_solver import solve

def execute(task):
    if not isinstance(task, dict):
        raise ValueError("Task must be a JSON object")

    name = task.get("task")
    params = task.get("parameters")

    if not isinstance(name, str):
        raise ValueError("Missing task name")

    if not isinstance(params, dict):
        raise ValueError("Missing parameters object")

    result = solve(name, **params)

    return {
        "task": name,
        "status": "SUCCESS",
        "result": result
    }

def run(input_file, output_file):
    task = json.loads(Path(input_file).read_text())
    try:
        result = execute(task)
    except Exception as exc:
        result = {
            "task": task.get("task") if isinstance(task, dict) else None,
            "status": "ERROR",
            "error": str(exc)
        }

    Path(output_file).write_text(
        json.dumps(result, indent=2),
        encoding="utf-8"
    )
    return result
