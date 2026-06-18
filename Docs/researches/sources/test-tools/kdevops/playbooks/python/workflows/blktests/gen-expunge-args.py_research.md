# sources/test-tools/kdevops/playbooks/python/workflows/blktests/gen-expunge-args.py

Purpose: generates blktests exclusion arguments or plain failure names from a results directory.

Important APIs/types/functions: `main` uses `argparse` options `--test-group`, `--gen-exclude-args`, `--verbose`, and positional `results`. It scans files with `os.walk` and emits either `group/test` lines or `-x group/test` arguments.

Control flow: collect `.bad` and `.dmesg` files, parse each path relative to the results directory as `<device>/<group>/<test>.<ext>`, filter by optional group, and print the requested format.

State/persistence behavior: read-only; no files are modified.

Dependencies/integration: feeds blktests `check` command invocations and expunge/debug workflows.

Risks/test signals: imports `subprocess` but does not use it; path parsing silently skips unexpected layouts. Test signals are deterministic output for known failed result trees and correct `-x` formatting when requested.
