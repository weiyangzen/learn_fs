# sources/storage-engines/foundationdb/contrib/local_cluster/binding_test.py

## Purpose
`binding_test.py` runs FoundationDB binding tester suites against a temporary local FoundationDB cluster. It is a harness for cycling API, concurrency, directory, HCA, and scripted binding tests across multiple language bindings.

## Important APIs, Types, And Functions
Constants derive default paths for `fdbserver`, `fdbcli`, `libfdb`, the binding tester script, and Python bindings. `_setup_logs`, `_setup_args`, and `_check_file` handle CLI setup. `TestSet` stores binding tester configuration and environment, sets the active cluster file, and exposes `run_scripted_test`, `run_api_test`, `run_api_concurrency_test`, `run_directory_test`, and `run_directory_hca_test`. `API_LANGUAGES` lists `python3`, `java`, `java_async`, `go`, `flow`, and `swift`. `_generate_test_list` builds callable test closures. `run_binding_tests` starts a local cluster and runs cycles. `main` validates paths, configures executable paths, constructs `TestSet`, and exits based on failure count.

## Control Flow
`main` parses args, configures logs and binary paths, creates a `TestSet`, then calls `asyncio.run(run_binding_tests(...))`. `run_binding_tests` creates a one-process `FDBServerLocalCluster`, sets the generated cluster file on the test set, runs all generated tests or one random test per cycle, counts failures, optionally stops after a configured threshold, and finally logs severity 40 and 30 cluster trace lines. Each test launches the binding tester as an async subprocess, waits with a per-test timeout, then drains and logs stdout/stderr.

## State And Persistence Behavior
Persistent external state is limited to the local cluster work directory, fdbserver data/log files, and any side effects from binding tests in the temporary database. The process environment for tester subprocesses is copied from `os.environ` and prepended with `LD_LIBRARY_PATH` and `PYTHONPATH`. Failure counts and cluster file path are in memory.

## Dependencies And Integration Points
It depends on sibling `lib.fdb_process`, `lib.local_cluster`, and `lib.process`, plus FoundationDB binaries, binding tester scripts, language runtimes, and libfdb shared libraries. It uses the local-cluster async context manager to provide a configured memory database.

## Risks And Edge Cases
`stop_at_failure` handling treats `-1` as truthy, so the default can trigger early-stop logic once failures exceed -1. `_test_coroutine` logs subprocess output but does not inspect process return code, so a failing binding tester can be reported successful if it exits before timeout. `_update_path_from_env` logs `LD_LIBRARY_PATH` even when updating `PYTHONPATH`. The local cluster is always one process. Random mode uses unseeded randomness.

## Test Signals
Tests should mock `lib.process.Process` and `FDBServerLocalCluster` to assert command arguments, environment setup, timeout handling, return-code handling if fixed, failure thresholds, random selection, and severity log extraction. Integration tests require packaged FDB binaries and binding tester runtimes.
