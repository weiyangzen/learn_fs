# sources/test-tools/kdevops/scripts/workflows/lib/blktests.py

## Purpose
Library routines for blktests watchdogs: process detection, last-test discovery, historical runtime lookup, config parsing, and host enumeration.

## Important APIs
`blktests_check_pid(host)` finds a remote `check` process and verifies its cwd has `tests`. `get_blktest_host(host, basedir, kernel, section, config)` returns `(last_test, last_test_time, current_time_str, delta_seconds, stall_suspect)`. `get_last_run_time()` reads prior runtime data. `get_config()`, `get_section()`, and `get_hosts()` parse kdevops config/inventory.

## Control flow
The host status function handles uname issues, missing last-test logs, SSH timeouts, missing running `check` process, then parses a `run blktests ... at ...` line. If watchdog config is enabled it compares elapsed time with either default new-test thresholds or historical runtime multiplied by configured factors.

## State and dependencies
Read-only over remote process/journal state and local `workflows/blktests/results/last-run/`. Depends on `lib.kssh`, `datetime`, `configparser`, and shell-style `.config` parsing.

## Integration points
Consumed by `blktests_watchdog.py`.

## Risks and test signals
`enable_watchdog` is a stripped string, so non-empty values such as `n` are truthy in Python. Runtime file search walks the whole last-run tree. Test with watchdog enabled/disabled configs and representative last-run files.
