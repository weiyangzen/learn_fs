# sources/storage-engines/rocksdb/include/rocksdb/perf_level.h

Purpose: This small public header defines the instrumentation level used by RocksDB performance counters. It controls how much data `perf_context` and `iostats_context` collect for the current thread.

Important APIs and types: `enum PerfLevel : unsigned char` defines `kUninitialized`, `kDisable`, `kEnableCount`, `kEnableWait`, `kEnableTimeExceptForMutex`, `kEnableTimeAndCPUTimeExceptForMutex`, `kEnableTime`, and sentinel `kOutOfBounds`. `SetPerfLevel(PerfLevel level)` sets the current thread's collection level. `GetPerfLevel()` returns it.

Control flow: Levels are incremental: enabling a higher level includes metrics from lower levels plus additional categories. Count/byte metrics start at `kEnableCount`; RocksDB-internal wait/delay metrics start at `kEnableWait`; operation timing starts at `kEnableTimeExceptForMutex`; CPU time starts at `kEnableTimeAndCPUTimeExceptForMutex`; mutex/condition timing starts at `kEnableTime`.

State and persistence behavior: The setting is runtime-only and thread-local. It does not persist in DB state and does not affect logical results, but higher levels add measurement overhead.

Dependencies and integration points: The header depends only on `rocksdb_namespace.h` plus standard types. `perf_context.h`, iostats collection, DB tests, benchmarking tools, and applications that need diagnostics call these APIs.

Risks and edge cases: `kOutOfBounds` must remain the last value. Metric names generally imply their enabling level, but comments in metric declarations are the source of truth for exceptions. Tests must avoid assuming metrics are populated when the level is too low.

Test signals: Unit tests should verify set/get behavior per thread, incremental metric enabling, disabled mode preserving zero/no-op counters, and boundary validation around `kOutOfBounds`.
