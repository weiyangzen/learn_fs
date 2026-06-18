# sources/storage-engines/rocksdb/buckifier/bench-slow.json

## Purpose

`bench-slow.json` is the slow ServiceLab/fancy-bench configuration set consumed by `buckifier/buckify_rocksdb.py` when generating RocksDB's `BUCK` file. It describes long-running RocksDB microbenchmark suites that are emitted as slow `fancy_bench_wrapper` targets by `TARGETSBuilder.add_fancy_bench_config`.

The file is a JSON array of 15 configuration objects named `rocksdb_microbench_suite_0` through `rocksdb_microbench_suite_14`. The buckifier appends `_slow` to each generated target name and passes `slow=True`, so the effective Buck target names are `rocksdb_microbench_suite_N_slow`.

## Structure and Important Fields

Each top-level object has the same shape:

- `name`: logical suite name, reused from the fast benchmark file but transformed to a slow Buck target name by the generator.
- `benchmarks`: nested mapping of benchmark binary name to benchmark case name to metric list.
- `expected_runtime_one_iter`: suite-level expected runtime used by the fancy-bench wrapper. Values cluster around 88709 to 88891, much larger than the fast file.
- `sl_iterations`: always `3`, so each ServiceLab run expects three iterations.
- `regression_threshold`: always `10`, expressing the regression threshold passed into the generated wrapper.

The nested `benchmarks` map covers two binaries:

- `db_basic_bench`: present in all 15 suites, with 37 or 38 benchmark cases per suite.
- `ribbon_bench`: present only in suites 8, 9, 11, 12, 13, and 14, with 10 to 13 cases where present.

Whole-file counts from structured inspection:

- 15 top-level suites.
- 631 total benchmark case entries.
- 631 overloaded metric objects containing `est_runtime`.
- Per-case estimated runtimes range from `1.194392` to `8213.664958`.
- Suite expected runtimes range from `88709` to `88891`.

Benchmark families include `DBClose`, `DBGet`, `DBOpen`, `DBPut`, `DataBlockSeek`, `IteratorNext`, `IteratorNextWithPerfContext`, `IteratorPrev`, `IteratorSeek`, `ManualFlush`, `PrefixSeek`, `RandomAccessFileReaderRead`, `SimpleGetWithPerfContext`, and ribbon filter families `FilterBuild`, `FilterQueryNegative`, and `FilterQueryPositive`.

Metric strings include common timing/size fields such as `real_time`, `cpu_time`, `threads`, `db_size`, `get_mean`, `put_mean`, `neg_qu_pct`, `fp_pct`, `seek_ns`, and `size`, plus slow-suite-specific RocksDB internal/perf-context fields such as `block_checksum_time`, `block_read_time`, `block_seek_nanos`, `find_next_user_entry_time`, `flush_time`, `flush_write_bytes`, `get_cpu_nanos`, `get_from_output_files_time`, `get_from_table_nanos`, `get_post_process_time`, `get_snapshot_time`, `internal_key_skipped_count`, `iter_next_cpu_nanos`, `new_table_block_iter_nanos`, and `user_key_comparison_count`.

## Control Flow and Integration

This JSON file has no executable control flow itself. Its operational flow is defined by `buckify_rocksdb.py`:

1. `generate_buck()` opens `buckifier/bench-slow.json`.
2. It parses the array with `json.load`.
3. It walks every suite, binary, benchmark case, and metric value.
4. It strips non-string metric entries by copying only metrics where `not isinstance(metric, dict)`. This removes the per-benchmark `{"est_runtime": ...}` objects from the generated Buck configuration.
5. It calls `BUCK.add_fancy_bench_config(config_dict["name"] + "_slow", clean_benchmarks, True, expected_runtime_one_iter, sl_iterations, regression_threshold)`.
6. `targets_builder.py` formats that data into a `fancy_bench_template` from `targets_cfg.py`.

The case names encode runtime parameters in a slash-separated benchmark-name format, for example `DBGet/comp_style:0/max_data:536870912/per_key_size:1024/...`. These strings are not parsed by the buckifier; they are preserved as keys and interpreted later by the benchmark binary/wrapper.

## State and Persistence

The file is static input data. It persists benchmark suite definitions in source control. At generation time, its contents are copied into generated `BUCK` output, except that per-case `est_runtime` objects are omitted and only string metrics remain in `bench_config`.

No local state is written by the JSON file itself. The persistence side effects happen in the buckifier: opening and rewriting the repository `BUCK` file.

## Dependencies

Direct dependencies are schema-level:

- `buckify_rocksdb.py` expects this file under `repo_path/buckifier/bench-slow.json`.
- Python's `json` module must parse it successfully.
- `TARGETSBuilder.add_fancy_bench_config` must accept the cleaned nested mapping.
- Benchmark binary names must correspond to binaries generated elsewhere, notably `db_basic_bench` and `ribbon_bench`.
- Benchmark case names and metric names must be meaningful to the ServiceLab/fancy bench infrastructure and the underlying RocksDB benchmark executables.

## Risks and Edge Cases

The most important integration risk is in the consumer, not in the JSON: the slow-file loop in `buckify_rocksdb.py` builds `clean_benchmarks` in one loop and then emits all slow configs in a second loop, so the final value from the first loop can be reused for every slow suite. That means all generated slow fancy-bench targets may receive the benchmarks from the last parsed suite while retaining each suite's own name/runtime metadata. This makes this file's per-suite distribution vulnerable to being flattened during BUCK generation.

Other risks:

- The buckifier catches all exceptions around both benchmark JSON files and silently skips fancy-bench generation. A malformed slow JSON file can remove generated benchmark targets without failing the buckifier.
- Per-case `est_runtime` values are deliberately removed before Buck emission. They are useful for curation and balancing but are not preserved in the generated `bench_config`.
- Suite names duplicate the fast file and rely on `_slow` suffixing for uniqueness. Any external consumer that does not mirror the suffix behavior can confuse fast and slow suites.
- The benchmark case keys are long strings with embedded parameters. There is no schema validation for parameter names, numeric ranges, or typo detection.
- Several slow cases are expensive by design, including `ManualFlush` cases around 7.4k to 8.2k estimated runtime and large `max_data:536870912` DB/iterator cases. Accidental promotion into a fast lane would be costly.

## Test Signals

Validation signals available from this repo:

- `jq` successfully parsed the file as JSON.
- Structured inspection found 15 suites, 631 benchmark entries, and the expected top-level fields.
- `check_buck_targets.sh` indirectly tests that this file and `buckify_rocksdb.py` generate a stable `BUCK` file.
- Functional validation requires running the buckifier and checking generated fancy-bench targets, especially that slow suites do not all share the same last-suite benchmark map.
