# sources/storage-engines/rocksdb/build_tools/regression_build_test.sh

## Purpose
This Bash script builds RocksDB in release mode, runs a fixed suite of `db_bench` performance benchmarks, stores benchmark output in temporary stat files, and reports selected throughput and latency metrics to Facebook ODS when running under Jenkins. When not under Jenkins, it prints the metric key/value pairs instead. The file is a regression/performance signal script rather than a unit test.

## Important APIs, types, and functions
The script uses `set -e` and a global `NUM=10000000` as the default key/write scale. It accepts one optional argument for `DATA_DIR` and a second optional argument for `STAT_FILE`; otherwise it creates temporary names via `mktemp`. `cleanup` deletes the database directory and all stat files matching `$STAT_FILE.*` and is installed as an EXIT trap.

Most of the script is a sequence of `./db_bench` invocations with explicit options. It exercises `fillseq`, `overwrite`, `readrandom`, `filluniquerandom`, `readwhilewriting`, `fillrandom`, `seekrandomwhilewriting`, and column-family-heavy configurations. Shared in-memory benchmark options are stored in `common_in_mem_args`.

`send_to_ods` accepts a metric key and value. Without `JENKINS_HOME`, it prints the pair. Under Jenkins, it sends the value to `https://www.facebook.com/intern/agent/ods_set.php` with entity `rocksdb_build` using `curl --silent --connect-timeout 60`. `send_benchmark_to_ods` parses a benchmark output file using `grep` and `awk` to derive QPS and p50/p75/p99 percentile latencies, then sends four metrics through `send_to_ods`.

## Control flow
The script chooses `DATA_DIR` and `STAT_FILE` from positional arguments or temp defaults, installs cleanup, and runs `make release` before any benchmark. It first fills a database with `fillseq`, measures overwrite, refills for read tests, and measures readrandom variants using 6 GB block cache, tailing iterators, 100 MB block cache, and a mixed overwrite/read case intended to leave data in memtable/SST state.

It then loads a smaller database using `filluniquerandom`, runs a dummy readrandom to compact or settle the data, measures readrandom with auto compactions disabled, and measures readwhilewriting with a write-rate limit. A memtable-focused benchmark runs `fillrandom,readrandom,` with a large write buffer and small value size.

The in-memory section defines a plain-table, no-compression, `/dev/shm/rocksdb` configuration with WAL in `/dev/shm`, fills roughly 50 million keys, and then runs 600-second `readwhilewriting` and `seekrandomwhilewriting` benchmarks with 32 threads. Finally, it measures `fillseq` and `overwrite` with 500 column families.

After all benchmark files are produced, the script calls `send_benchmark_to_ods` for each expected output file, mapping benchmark names to ODS metric suffixes such as `rocksdb.build.overwrite.qps`, `rocksdb.build.readrandom_tailing.p99_micros`, and `rocksdb.build.seekwhilewriting_in_ram.p50_micros`.

## State and persistence behavior
The script creates and deletes a RocksDB data directory and stat files. By default, both are under `mktemp` locations, but callers can supply persistent paths. Cleanup removes the entire `$DATA_DIR` and `$STAT_FILE.*` on exit, including failures. The in-memory benchmarks use a hard-coded `/dev/shm/rocksdb` database and WAL directory through `common_in_mem_args`; this is not controlled by `DATA_DIR` and may overwrite or conflict with other users of that path.

Benchmark output is persisted only until cleanup unless the script is interrupted in a way that bypasses the EXIT trap. ODS reporting is external network state when `JENKINS_HOME` is set; otherwise results are printed locally. The script does not maintain a local historical baseline.

## Dependencies and integration points
The script depends on Bash, `make release`, the built `./db_bench` binary, `grep`, `awk`, `curl`, `mktemp`, sufficient disk space for `$DATA_DIR`, and enough RAM-backed storage for `/dev/shm/rocksdb`. It integrates with Jenkins through `JENKINS_HOME` and with Facebook's internal ODS endpoint. It assumes `db_bench` output format contains the benchmark line with QPS in field 5 and a "Percentiles" line within six following lines with percentile fields in fixed positions.

## Risks and edge cases
The benchmark suite is resource-intensive. It uses 10 million operations for many disk-backed runs, a 6 GB cache size, 55,000 open files, 16 to 32 threads, 600-second in-memory runs, and a 50-million-key `/dev/shm` database. Small CI hosts can fail due to memory, tmpfs capacity, file descriptor limits, runtime limits, or noisy-neighbor performance variance.

Argument validation is minimal. Supplying only two arguments works, but extra arguments are ignored. Variable expansions such as `$DATA_DIR`, `$STAT_FILE`, `$JENKINS_HOME`, and the ODS URL parameters are mostly unquoted, which can misbehave with paths or values containing whitespace or shell metacharacters. Cleanup uses `rm -rf $DATA_DIR`, so an incorrectly supplied or empty `DATA_DIR` would be dangerous; defaults are safer but caller-provided values require care.

The parser in `send_benchmark_to_ods` is brittle. If `db_bench` output changes, if a benchmark name appears in multiple contexts, or if the "Percentiles" layout changes, QPS or latency values may be empty or wrong. Under Jenkins, `send_to_ods` checks for empty values and reports an error, but it does not fail the script. The hard-coded internal ODS endpoint is not useful outside Meta/Facebook infrastructure.

The in-memory benchmarks ignore the cleanup trap's `$DATA_DIR` removal and instead use `/dev/shm/rocksdb`; if `db_bench` does not clean that path between runs, stale RAM-backed data could affect results or consume tmpfs. The script also disables WAL in many disk benchmarks, so metrics target specific RocksDB configurations rather than end-user durability defaults.

## Test signals
Syntax validation can be done with `bash -n build_tools/regression_build_test.sh`. Functional validation is expensive: `make release` must succeed, `./db_bench` must exist and complete every configured run, expected stat files must be non-empty, and local non-Jenkins output should print metric keys and values. Under Jenkins, network calls to ODS should return successfully and keys should appear in the expected `rocksdb.build.*` namespace. A smaller manual smoke test would require editing `NUM` or wrapping `db_bench`, because the script itself has no fast-mode option.
