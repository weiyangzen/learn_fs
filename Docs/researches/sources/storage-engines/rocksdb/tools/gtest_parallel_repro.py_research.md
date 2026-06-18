<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/gtest_parallel_repro.py -->
# sources/storage-engines/rocksdb/tools/gtest_parallel_repro.py

## Purpose
`gtest_parallel_repro.py` repeatedly runs many fresh instances of a GoogleTest binary in parallel to reproduce flakes caused by process-level scheduling pressure, CPU starvation, or timing assumptions that do not appear in single-process `--gtest_repeat` loops.

## Important APIs, Types, and Functions
- Regexes `FAILURE_LINE_RE`, `SANITIZER_RE`, and `ASSERT_RE` extract failure keys from logs.
- Argument helpers include `positive_int()`, `parse_env()`, `resolve_cpu_list()`, and grouped parser builders for gtest, run control, output, CPU, and build flags.
- `build_if_requested()` optionally runs `make clean` and `make`, adding `COERCE_CONTEXT_SWITCH=1` when requested.
- `make_run_command()` builds the binary invocation and wraps it in `taskset -c` when CPU pinning is requested.
- Process lifecycle helpers include `launch_process()`, `launch_iteration_processes()`, `monitor_processes()`, `terminate_process()`, `terminate_processes()`, and `close_log_handles()`.
- Result helpers include `extract_failure_keys()`, `collect_process_result()`, `collect_iteration_results()`, `write_jsonl()`, `merge_histogram()`, and `print_summary()`.
- `prepare_run()` validates args, builds if needed, resolves CPU command, creates output directory, and writes `metadata.json`.
- `run_iterations()` runs the requested number of iterations, handles KeyboardInterrupt, supports `--stop-on-failure`, and returns failures plus histograms.

## Control Flow
`main()` parses arguments, prepares the run, prints command/output metadata, executes `iteration_count` batches of `processes_per_iteration` concurrent processes, writes `failures.jsonl`, prints totals and the top failure histogram, and returns one if failures occurred, zero if none occurred, or 130 if interrupted.

Each process gets its own run directory with `tmp/` assigned as `TEST_TMPDIR` and a combined stdout/stderr `log.txt`. After monitoring, successful run directories are deleted unless `--keep-success-artifacts` is set; failed or timed-out directories are retained and summarized.

## State and Persistence Behavior
Run state is written under `--out` or `/tmp/gtest_parallel_repro_<time>`. Persistent files include `metadata.json`, `failures.jsonl`, retained failure run directories, logs, and per-process `TEST_TMPDIR` contents. Successful artifacts are normally removed to keep output size bounded.

## Dependencies and Integration Points
The script uses only Python stdlib plus external `make`, the requested gtest binary, and optional `taskset`. It integrates with GoogleTest flags, environment overrides, RocksDB's optional `COERCE_CONTEXT_SWITCH` build mode, Unix process groups, and CPU affinity.

## Risks and Edge Cases
- `--out` must be empty if it exists, preventing accidental mixing of runs.
- `taskset` is required for `--cpus` or `--cpu-count`; unavailable taskset becomes a parser error.
- Timeout termination uses process groups where possible; binaries that spawn outside the group can escape.
- Failure-key extraction is heuristic and may group unrelated non-gtest failures under `<non-gtest failure>`.
- `--coerce-context-switch` only affects builds performed by this script; it warns but cannot verify an existing binary was built with that flag.

## Test Signals
The tool's own signal is exit status and generated summary. `TOTAL_RUNS`, `TOTAL_FAILURES`, `FAILURES_FILE`, and `FAILURE_HISTOGRAM` summarize reproduction quality. Retained logs and JSONL records provide per-process return code, elapsed time, log path, and failure keys.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/gtest_parallel_repro.py -->
