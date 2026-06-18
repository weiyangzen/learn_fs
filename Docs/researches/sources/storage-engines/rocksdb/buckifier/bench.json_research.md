# sources/storage-engines/rocksdb/buckifier/bench.json

## Purpose

`bench.json` is the fast RocksDB ServiceLab/fancy-bench configuration file used by `buckifier/buckify_rocksdb.py`. It defines shorter microbenchmark suites that are embedded into generated `BUCK` output as non-slow fancy-bench targets.

The file is a JSON array of 15 suites named `rocksdb_microbench_suite_0` through `rocksdb_microbench_suite_14`. Unlike `bench-slow.json`, the buckifier does not suffix the names and passes `slow=False` to `add_fancy_bench_config`.

## Structure and Important Fields

Every suite object contains:

- `name`: generated Buck target/config name.
- `benchmarks`: nested map from binary to benchmark case to metric list.
- `expected_runtime_one_iter`: suite-level expected runtime, mostly `2437` or `2438`, with suites 2 and 11 at `2446`.
- `sl_iterations`: always `3`.
- `regression_threshold`: always `10`.

Whole-file counts from structured inspection:

- 15 top-level suites.
- 149 total benchmark case entries.
- 149 overloaded metric objects containing `est_runtime`.
- Per-case estimated runtimes range from `1.194392` to `696.590699`.
- Two binaries are referenced: `db_basic_bench` and `ribbon_bench`.

`db_basic_bench` appears in all 15 suites. It covers `DBGet`, `DBPut`, `DataBlockSeek`, and `RandomAccessFileReaderRead`. `ribbon_bench` appears in 13 suites and covers `FilterBuild`, `FilterQueryNegative`, and `FilterQueryPositive`.

The metric vocabulary is narrower than the slow file: `real_time`, `cpu_time`, `threads`, `db_size`, `get_mean`, `put_mean`, `neg_qu_pct`, `fp_pct`, `seek_ns`, and `size`.

## Control Flow and Integration

The file is read in the first benchmark-configuration block of `generate_buck()`:

1. Open `repo_path/buckifier/bench.json`.
2. Parse JSON into `fast_fancy_bench_config_list`.
3. For each suite, walk `benchmarks` by binary and benchmark case.
4. Build `clean_benchmarks` by copying only string metrics and dropping dictionary entries such as `{"est_runtime": 510.387506}`.
5. Call `BUCK.add_fancy_bench_config(name, clean_benchmarks, False, expected_runtime_one_iter, sl_iterations, regression_threshold)`.
6. `TARGETSBuilder` pretty-prints the nested map into a generated `fancy_bench_wrapper` target.

The buckifier treats benchmark case keys as opaque strings. Parameterized names such as `DBPut/comp_style:1/max_data:107374182400/per_key_size:256/enable_statistics:1/wal:1/iterations:51200/threads:8` are preserved and passed through to the benchmark runner.

## State and Persistence

The JSON file persists curated fast benchmark suites in source control. It does not write state by itself. During BUCK generation, its cleaned benchmark map and suite metadata are appended to `BUCK`; the per-case `est_runtime` dictionaries are not emitted as metrics.

## Dependencies

Key dependencies and integration points:

- Consumed only when `buckify_rocksdb.py` can find it under `buckifier/bench.json`.
- Requires valid JSON and the expected object schema.
- Depends on generated binaries named `db_basic_bench` and `ribbon_bench`.
- Depends on `TARGETSBuilder.add_fancy_bench_config` and `targets_cfg.fancy_bench_template`.
- The downstream fancy-bench wrapper and benchmark executables must understand the parameterized case names and selected metric names.

## Risks and Edge Cases

- Any schema drift is only caught at buckifier runtime. Because benchmark parsing sits inside a broad `except Exception: pass`, parse or key errors can silently remove all fancy-bench targets.
- `est_runtime` is stored per case but filtered out for generated configs. Runtime balancing logic therefore lives outside the generated target's metric list.
- There is no validation that suite expected runtimes match the sum or max of per-case `est_runtime`; the suite-level `expected_runtime_one_iter` values are manually curated constants.
- The file reuses the same suite-name range as `bench-slow.json`. The fast file relies on the slow file adding `_slow` to avoid target collisions.
- Benchmark case names are manually encoded strings; typos in parameters like `comp_style`, `max_data`, `enable_filter`, or `iterations` would pass JSON validation and only fail or skew measurements later.

## Test Signals

Available validation signals:

- `jq` parsed the file and confirmed 15 suite objects and 149 benchmark case entries.
- The buckifier fast loop emits each suite immediately after cleaning, so per-suite benchmark maps are preserved in generated output.
- `check_buck_targets.sh` can detect when edits to this file require regenerating `BUCK`.
- Meaningful behavioral validation requires generating `BUCK` and inspecting or running the resulting `rocksdb_microbench_suite_N` fancy-bench targets.
