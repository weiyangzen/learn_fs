# sources/storage-engines/foundationdb/contrib/Joshua/scripts/correctnessTest.sh

Purpose: Joshua entrypoint for TestHarness2 correctness runs in containerized FoundationDB testing. It validates `JOSHUA_SEED`, builds `python3 -m test_harness.app` arguments, captures stdout/stderr, and guarantees Joshua receives XML even when Python crashes before normal output.

Important APIs and control flow: shell environment variables are the API. Required input is `JOSHUA_SEED`; optional knobs include `JOSHUA_TEST_FILES_DIR`, `OLDBINDIR`, `TH_ARCHIVE_LOGS_ON_FAILURE`, preservation flags, output location, buggify/valgrind/long-running settings passed indirectly through TestHarness2. The script creates a unique `th_run_*` directory, runs TestHarness2 with `--no-clean-up` and `--no-verbose-on-failure`, tees stdout to `python_app_stdout.log`, and derives exit status from Python exit plus `Ok="0"` in captured XML.

State and persistence: test artifacts live under `TH_OUTPUT_DIR`, `DIAG_LOG_DIR`, or `/tmp`. Cleanup is trap-based and preserves or deletes the run directory based on success, Python exit, XML failure, and archival environment settings.

Dependencies and integration: depends on bash, `python3`, `tee`, TestHarness2 importability, Joshua env vars, and optional `test_args.txt`. It integrates with Joshua by producing single-line XML results and with `test_harness.app` by passing run temp and binary paths.

Risks and test signals: XML failure detection is a grep over stdout and can miss JSON mode or altered formatting. Cleanup references `PYTHON_EXIT_CODE` before assignment if an early exit occurs. Strong test signals include missing-seed fallback XML, empty-output fallback XML, preserved logs on failure, and shell exit code consistency with `Ok`.
