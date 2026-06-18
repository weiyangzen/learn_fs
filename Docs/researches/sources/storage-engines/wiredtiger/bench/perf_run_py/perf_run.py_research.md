# sources/storage-engines/wiredtiger/bench/perf_run_py/perf_run.py

## Purpose
This is the main Python harness for running WiredTiger wtperf/workgen performance tests, collecting selected metrics, and writing brief Evergreen-compatible or detailed Atlas-compatible JSON output.

## Important APIs, Types, and Functions
Important functions include `create_test_home_path`, `construct_command_line`, `configure_for_extra_accuracy`, `run_test_wrapper`, `run_test`, `process_results`, `parse_args`, `parse_json_args`, `validate_operations`, `run_perf_tests`, `report_results`, and `main`. It uses `PerfConfig`, `TestType`, `PerfStat`, and `PerfStatCollection`.

## Control Flow
`main` parses CLI flags, converts JSON arguments/operations, validates duplicate/unknown operations, runs one or more tests unless `--reuse` is set, processes stat files from generated home directories, and writes/prints JSON results. Batch mode reads a JSON list of argument/operation sets and processes each with an index-specific home prefix. Extra accuracy mode forces `run_max = 5` and tries to inject `run_time=240`.

## State, Persistence, and Dependencies
Persistent state includes per-run home directories, `stdout_file.txt`, and the output JSON path. Dependencies include `argparse`, `subprocess`, `psutil`, `platform`, local perf modules, and test executables. It captures stdout/stderr together and exits on subprocess failure.

## Integration Points, Risks, and Test Signals
It bridges executable workloads, stat extraction, and CI performance formats. Risks include JSON argument quoting, batch mode mutating `config.run_max` for later entries, `configure_for_extra_accuracy` returning `None` on one branch, use of `list.index` for duplicate batch entries, and overwriting `stdout_file.txt`. Signals are subprocess success and populated metrics matching requested operation labels.
