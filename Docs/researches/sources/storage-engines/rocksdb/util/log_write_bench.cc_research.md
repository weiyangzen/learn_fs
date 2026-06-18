# sources/storage-engines/rocksdb/util/log_write_bench.cc

Purpose: implements a small gflags-based benchmark that simulates transactional log writes by repeatedly appending fixed-size records, flushing, optionally syncing, pacing writes, and reporting append-plus-flush latency distribution.

Important APIs/types/functions: command-line flags are `num_records`, `record_size`, `record_interval`, `bytes_per_sync`, and `enable_sync`. `RunBenchmark` creates a per-thread log path, configures `EnvOptions` through `Env::OptimizeForLogWrite`, constructs `WritableFileWriter`, appends records, calls `Flush` and optional `Sync`, records `HistogramImpl` latency, and sleeps to maintain the requested interval. Without gflags, `main` prints an install message and exits with code 1.

Control flow: the benchmark parses flags, calls `RunBenchmark`, opens a writable log file, builds a record filled with `X`, then loops `num_records` times. Each iteration measures append/flush/sync latency, periodically prints progress, computes schedule drift from the original start time, and sleeps if ahead of schedule. At the end it prints histogram text to stderr.

State and persistence behavior: writes a temporary benchmark log file under `test::PerThreadDBPath("log_write_benchmark.log")`. It does not delete the file in this source. Runtime state includes writer buffers, histogram buckets, timing values, and configured `bytes_per_sync`.

Dependencies/integration points: depends on gflags compatibility, `WritableFileWriter`, RocksDB `Env`, system clock, `DBOptions`, histogram implementation, and test utilities for per-thread paths. It exercises the same writable-file abstraction used by WAL/log writing paths, but as a standalone tool.

Risks: several I/O statuses are ignored, including file creation, append, flush, and sync results, so benchmark output can be misleading on failures. Pacing uses a simple cumulative schedule and can skip sleeps when writes fall behind. The no-gflags build is only a stub. The benchmark is not a correctness test and may leave files behind.

Test signals: no automated assertions. Useful signals are runtime stderr progress and the final latency histogram when invoked manually with gflags.
