# sources/test-tools/kdevops/workflows/build-linux/Makefile

## Purpose
Exposes build-linux targets for running repeated kernel builds, collecting results, visualizing output, and managing monitoring data.

## Important APIs, Types, and Functions
Targets are `build-linux`, `build-linux-baseline`, `build-linux-dev`, `build-linux-results`, `build-linux-visualize`, `monitor-results`, `monitor-kill`, and `build-linux-help-menu`. It uses `KDEVOPS_NODES`, `ANSIBLE_INVENTORY_FILE`, `KDEVOPS_EXTRA_VARS`, and `LIMIT_HOSTS`.

## Control Flow
`build-linux` runs the main playbook, then invokes result collection and visualization. Visualization checks that `workflows/build-linux/results` is non-empty, optionally generates summaries, and runs `visualize_results.py`.

## State and Persistence Behavior
Artifacts persist under `workflows/build-linux/results/`: logs, raw timing data, summaries, HTML, and monitoring images.

## Dependencies and Integration Points
Integrates with `build_linux.yml`, `build_linux_results.yml`, monitoring playbooks, `generate_summaries.py`, and `visualize_results.py`.

## Risks and Edge Cases
The visualization path is hard-coded and may ignore `BUILD_LINUX_RESULTS_DIR`. `HOSTS="baseline"`/`"dev"` relies on outer Makefile plumbing. Summary generation warnings can defer failures to visualization.

## Test Signals
Run `make -n` targets with empty and populated results directories. Use a one-build result set to verify summary generation and `html/index.html`.
