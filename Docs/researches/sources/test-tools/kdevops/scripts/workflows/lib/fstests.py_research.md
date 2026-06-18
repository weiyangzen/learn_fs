# sources/test-tools/kdevops/scripts/workflows/lib/fstests.py

## Purpose
Library routines for fstests watchdogs, including running-process checks, current test discovery, stall estimation, soak-duration handling, config parsing, and inventory host extraction.

## Important APIs
`fstests_check_pid(host)`, `fstests_test_uses_soak_duration(testname)`, `get_fstest_host(use_remote, use_ssh, host, basedir, kernel, section, config)`, `get_checktime(host, basedir, kernel, section, last_test)`, `get_config(dotconfig)`, `get_section(host, config)`, and `get_hosts(hostfile, hostsection)`.

## Control flow
`get_fstest_host()` chooses SSH or systemd-remote journal based on config/options, parses the last `run fstests ... at ...` line, ignores completed sentinel tests, computes elapsed seconds, loads configured watchdog thresholds, adds soak duration for known soak tests, and marks stalls when elapsed time exceeds threshold outside start/end sentinels.

## State and dependencies
Read-only over remote process/journal state and local `workflows/fstests/results/<host>/<kernel>/<section>/check.time`. Depends on `lib.kssh`, `lib.systemd_remote`, `datetime`, and `configparser`.

## Integration points
Consumed by `fstests_watchdog.py`.

## Risks and test signals
Like blktests, stripped config strings are truthy even if value is `n`. The soak test list is hard-coded and can go stale. Test with SSH and remote journal modes, timezone-suffixed timestamps, missing `check.time`, and soak tests.
