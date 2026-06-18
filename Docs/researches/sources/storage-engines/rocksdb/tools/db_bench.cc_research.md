<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/db_bench.cc -->
# sources/storage-engines/rocksdb/tools/db_bench.cc

## Purpose
This file is the executable wrapper for RocksDB's `db_bench` benchmark tool. It gates real benchmark execution on gflags availability and delegates to the shared benchmark implementation.

## Important APIs, Types, and Functions
Without `GFLAGS`, it includes `<cstdio>` and defines `main()` to print `Please install gflags to run rocksdb tools` to stderr and return `1`. With `GFLAGS`, it includes `rocksdb/db_bench_tool.h` and defines `main(int argc, char** argv)` to return `ROCKSDB_NAMESPACE::db_bench_tool(argc, argv)`.

## Control Flow
The compile-time `#ifndef GFLAGS` branch selects either a stub executable or a thin delegating executable. In gflags-enabled builds all command-line parsing, benchmark selection, DB setup, workload execution, statistics, and cleanup are performed by `db_bench_tool`.

## State and Persistence Behavior
This wrapper has no benchmark state of its own. In the stub path it only writes an error message. In the real path, all DB files, benchmark state, and output behavior are owned by the delegated benchmark implementation.

## Dependencies and Integration Points
The wrapper integrates the build target named `db_bench` with the reusable API declared in `rocksdb/db_bench_tool.h`. It depends on gflags for the full tool, and on `ROCKSDB_NAMESPACE` for namespace selection. This pattern matches other RocksDB tool wrappers that keep executable `main` functions small while allowing tests or alternate frontends to call the implementation function.

## Risks and Edge Cases
Users can build a nonfunctional stub if gflags is missing. The wrapper performs no preflight checks, stack-trace setup, or argument normalization, so any such behavior must live in `db_bench_tool`. Signature or namespace changes to the benchmark implementation will break this entry point.

## Test Signals
There are no direct tests in this file. Build/link success in a gflags-enabled configuration confirms the wrapper sees `db_bench_tool`, and runtime benchmark tests or smoke runs exercise the delegated implementation. In non-gflags builds the expected signal is exit code `1` with the missing-gflags message.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/tools/db_bench.cc -->
