# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/create_package_runtime_table.sh

Purpose: renders e2e package runtime statistics as a Rich terminal table. It is invoked by the improved e2e runner after package execution to visualize package attempts, wait time, run time, and pass/fail/flaked status.
Important APIs/functions: shell `main` validates one input file, creates a temp venv, writes an embedded Python script, installs `python3-dev`, `python3-venv`, and `rich`, then executes the Python visualizer. Python groups lines by package and bucket type and renders `Table` columns for package, bucket, time, timeline, and status.
Control flow: the shell validates arguments and file existence before venv setup. Python parses space-separated records with fields package, bucket type, exit code, start seconds, and end seconds; invalid short rows are ignored. Runtime bars are built from sorted attempts using wait and run segments.
State and persistence: only temporary venv/script state is persisted during execution and removed by `trap`. Input data is read-only; no test logs are modified.
Dependencies and integration points: depends on repo `perfmetrics/scripts/os_utils.sh`, Python 3 venv support, pip/PyPI access, terminal width detection, and the runtime stats file produced by `improved_run_e2e_tests.sh`.
Risks and edge cases: installing system packages and pip dependencies during reporting can fail or slow CI; failures intentionally print warnings and skip visualization. Input parsing assumes package names and bucket types have no spaces.
Test signals: useful output is a table where green pass, yellow flake, red failure, and timeline bars reflect the stats file. Exit 0 on prerequisite failure means report rendering is non-critical.
