# sources/storage-engines/foundationdb/bindings/bindingtester/run_binding_tester.sh

## Purpose
This Bash script repeatedly runs FoundationDB binding tester suites across configured language testers, records failures to an error log, and supports random/test-indexed execution.

## Important APIs, Types, And Functions
Environment variables configure operations, HCA operations, concurrency, binding list, break-on-error, test selection, logging, and output capture. Functions include `logError`, `runCommand`, `runScriptedTest`, and `runTest`. Test types are API, concurrent API, Directory, and Directory HCA.

## Control Flow
The script requires cycle count and error-file arguments, initializes runtime state, optionally selects one random binding/test type, optionally runs scripted tests, then loops cycles until max cycles or failure policy stops it. `runCommand` captures output, times commands, logs failures, and increments status. `runTest` invokes `bindingtester.py` with appropriate flags for each selected test type.

## State And Persistence Behavior
It writes an error log and optional console log, reads environment variables, and runs tests against the default cluster settings used by `bindingtester.py`. It does not modify source files.

## Dependencies And Integration Points
It depends on Bash, `python3`, `bindingtester.py`, language tester artifacts, and a reachable FoundationDB cluster. It is a higher-level orchestration wrapper for the Python driver.

## Risks And Edge Cases
The default `BINDINGTESTS` includes `python3`, but `known_testers.py` registers `python`; this may rely on fallback command behavior or fail if no command exists. `LOGSTDOUT` appends to one console log and then reads the entire file into memory on each command. The cycle loop can run forever when max cycles is zero.

## Test Signals
Console output reports pass/fail per command, cycle summaries, failed test count, and error count; the error file captures command output for failures.
