# sources/test-tools/fio/t/fiotestlib.py

## Purpose
Defines the shared Python test framework used by many fio regression scripts to run fio binaries, job files, and command-line jobs while collecting artifacts and checking expected process/output behavior.

## Important APIs, Types, and Functions
`FioTest` owns common paths, artifact filenames, setup, and pass/fail state. `FioExeTest` runs a generic executable with timeout handling and checks return code/stderr expectations. `FioJobFileTest` wraps fio job files, optional preconditioning jobs, output-format selection, and JSON parsing. `FioJobCmdTest` builds command-line fio invocations, reads JSON output, reads IOPS logs, and validates data-direction emptiness through `check_empty()` and `check_all_ddirs()`. `run_fio_tests()` is the central table-driven runner.

## Control Flow
Test scripts pass dictionaries describing test class, ID, fio options, job files, requirements, and success policy. `run_fio_tests()` applies skip filters, constructs the right test object, checks requirements unless disabled, calls `setup()`, `run()`, and `check_result()`, then reports and optionally removes per-test artifacts. `FioExeTest.run()` uses `subprocess.Popen` instead of `subprocess.run()` so timeout cleanup can terminate fio more gracefully.

## State and Persistence Behavior
Every test writes command, stdout, stderr, exitcode, and often fio output files under `artifact_root/<test_id>`. Parsed JSON and IOPS logs are stored in object fields for subclass checks. The runner mutates configs by supplying a default success policy for command tests.

## Dependencies and Integration Points
Integrates all fio Python tests with the fio executable, fio job files under `t/jobs`, common requirement callbacks, platform-specific Python invocation on Windows, and artifact cleanup behavior.

## Risks
JSON extraction assumes output contains lines from the first `{` through the last `}`, which fails for malformed or empty output and can mis-handle braces in non-JSON text. `FioExeTest.run()` asserts `proc.poll()` after `terminate()`, which assumes prompt process exit. Test configs are mutable and can leak changes across repeated runs. Only stderr size and return code are checked generically, so deeper semantic validation must be supplied by subclasses.

## Test Signals
Framework signals include timeout behavior, nonzero/stderr success policies, JSON decoding with leading informational lines, precondition failure propagation, Windows script invocation, requirement-based skips, pass-through arguments, and artifact cleanup.
