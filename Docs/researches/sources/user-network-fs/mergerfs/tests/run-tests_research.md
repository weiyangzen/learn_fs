# sources/user-network-fs/mergerfs/tests/run-tests

## Purpose
Discovers and runs every `TEST_*` script with timeout, skip, pass, and fail reporting.

## Important APIs, Types, and Functions
The script scans its own directory with `os.scandir()`, launches each file whose name starts with `TEST_` via `subprocess.Popen`, enforces a 120 second timeout, and treats return code 77 as skip.

## Control Flow
For each test it prints the name, waits for completion, decodes combined stdout/stderr, records failures, kills timed-out children, and exits with status 1 if any test failed.

## State and Persistence Behavior
It does not create persistent state directly, but child tests create temporary mount trees. Output is printed to stdout for CI or local runs.

## Dependencies and Integration Points
Depends on executable `TEST_*` scripts and Python's subprocess module. It is the suite-level entrypoint for the mergerfs Python parity tests.

## Risks and Edge Cases
Directory scan order is filesystem-dependent. A hung cleanup can consume the timeout. Non-executable or non-Python `TEST_*` files would fail at process launch.

## Test Signals
Run with a known passing test, a synthetic skip, a failing script, and a timeout case to validate aggregate exit status.
