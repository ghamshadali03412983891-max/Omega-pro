# Physical Engineering AI Agent

Offline deterministic engineering task-processing harness.

## Supported tasks

1. beam
2. concrete
3. axial_stress
4. torque
5. electrical

## Run a JSON task

python run_agent.py --input task.json --output result.json

## Process inbox files

python run_agent.py --inbox inbox --outdir outputs

## Main files

- agent_harness.py
- run_agent.py
- solvers/engineering_solver.py
- reports/final_test_report.json
- final_manifest.json

## Limitations

This package is an offline deterministic solver harness.
It is not an LLM-based autonomous reasoning system.
The official competition evaluator protocol has not been verified.
No competition submission or prize result is guaranteed.
Engineering outputs require suitable assumptions and independent review.
