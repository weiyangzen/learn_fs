# sources/test-tools/fio/t/verify-trim.py

## Purpose
`verify-trim.py` is a Python 3 fio regression harness for the verify-trim path. It checks that fio emits trim operations alongside verified writes for sequential and random write workloads, validates trim count accounting from JSON output, and verifies that readonly mode rejects trim-producing configurations.

## Important APIs, Types, and Functions
The main type is `VerifyTrimTest`, a `fiotestlib.FioJobCmdTest` subclass. `setup()` builds a single fio command named `verifytrim` with `--verify=md5`, a caller-selected target filename, `--rw`, `--trim_percentage`, `--trim_backlog`, and optional entries from `VERIFY_OPT_LIST`. `check_result()` delegates base result parsing, then for JSON output compares `jobs[0].trim.total_ios` against `write.total_ios * trim_percentage / 100` with a 10 percent tolerance. `parse_args()` exposes fio path, fio root, artifact root, skip/run-only controls, requirement skipping, and `--dut`. `main()` provisions artifacts, resolves fio paths, checks requirements, optionally creates a Linux `null_blk` device with discard support, injects the chosen device into every test case, and runs `run_fio_tests()`.

## Control Flow and State
State is concentrated in `TEST_LIST` dictionaries and the artifact directory created for each run. If no device is provided, `main()` removes any existing `null_blk`, loads `null_blk memory_backed=1 discard=1`, uses `/dev/nullb0`, and removes the module afterward. Each test mutates `test['fio_opts']['filename']` before dispatch.

## Dependencies and Integration Points
It imports `FioJobCmdTest`, `run_fio_tests`, `SUCCESS_NONZERO`, and `Requirements` from fio's Python test framework. Runtime integration depends on Linux, `sudo modprobe`, `/dev/nullb0`, the fio binary, and JSON output shape from fio.

## Risks and Test Signals
Risks include privilege requirements, global `null_blk` module churn, tolerance masking small trim-count bugs, and cleanup not running if the process is killed hard. Test signals are nonzero exit count, base `FioJobCmdTest` pass/fail state, stderr/stdout/output dumps on failure, and JSON trim/write totals.
