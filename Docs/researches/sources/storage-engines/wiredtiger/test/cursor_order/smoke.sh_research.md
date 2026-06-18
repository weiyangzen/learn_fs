# sources/storage-engines/wiredtiger/test/cursor_order/smoke.sh

## Purpose

`smoke.sh` is the shell-level smoke test for the WiredTiger `cursor_order` executable. It runs the cursor-order workload in the two key table formats covered by the test: row-store keys and variable-length column-store record numbers. Its role is quick "make check" coverage rather than exhaustive stress configuration.

## Important commands and environment

- `#!/bin/sh` keeps the script portable across POSIX shell environments used by the WiredTiger test harness.
- `set -e` makes the script fail immediately if either workload invocation exits non-zero.
- `$TEST_WRAPPER ./cursor_order -tr` runs the executable through an optional harness wrapper for the row-store case.
- `$TEST_WRAPPER ./cursor_order -tv` runs the executable through the same wrapper for the variable-length column-store case.
- The script prints a short label before each run so logs identify which format was executing when a failure occurred.

`TEST_WRAPPER` is expected to be provided by the surrounding build/test environment when needed. If it is unset, POSIX shell expansion leaves a leading empty word and the command runs as `./cursor_order ...`, which is appropriate for direct local execution.

## Control flow

The script has a linear two-step flow. It first announces "cursor_order: rows" and invokes the binary with `-tr`. If that command succeeds, it announces "cursor_order: variable-length columns" and invokes the binary with `-tv`. Because `set -e` is active, a failure in the first command prevents the second from running, and a failure in either command becomes the script's exit status.

The `-t` option is parsed by `cursor_order.c`, where `r` selects `ROW` and `v` selects `VAR`. The rest of the workload uses defaults from the main driver unless overridden elsewhere: one append writer, five reverse scanners, one run, a default key count and operation count, and a single shared file.

## State and persistence behavior

This script does not create persistent state itself. Each executable invocation manages its own WiredTiger home through the test utility driver, creates or recreates test objects, loads records, runs concurrent scanner/writer operations, verifies the files, and shuts down the WiredTiger connection. The two invocations are separate processes, so in-memory state such as `SHARED_CONFIG`, `run_info`, thread counters, and the WiredTiger connection is not shared between the row and variable-column smoke runs.

## Dependencies and integration points

The script depends on the `cursor_order` binary being built in the current working directory or otherwise reachable as `./cursor_order`. It is designed for the WiredTiger test harness, where `TEST_WRAPPER` may inject tools such as environment setup, timeout handling, sanitizer runners, or platform-specific launch wrappers.

The adjacent `CMakeLists.txt` defines equivalent `test_cursor_order` variants named `row|-tr` and `var|-tv` and labels them for `check`. This script mirrors those two minimal configurations for make-check-style smoke testing.

## Risks and edge cases

- If `cursor_order` has not been built in the script's current directory, the first command fails immediately.
- Because `TEST_WRAPPER` is unquoted, wrappers that require embedded spaces or shell metacharacters depend on intentional shell word splitting by the harness.
- The smoke test covers only default row and variable-column configurations. It does not exercise multiple files, varied operation counts, different writer/scanner counts, longer reverse scans, repeated runs, custom WiredTiger open configuration, or explicit working directories.
- `set -e` gives fast failure but means the second variant is skipped after a row-store failure, so a single smoke run may expose only the first failing format.

## Test signals

The script's success signal is a zero exit status after both invocations complete. Useful log signals are the two echoed labels followed by the executable's own process, thread start/stop, timer, statistics, and verification output. A non-zero exit from either `cursor_order` run indicates a workload assertion failure, WiredTiger/test utility error, missing binary, or wrapper failure.
