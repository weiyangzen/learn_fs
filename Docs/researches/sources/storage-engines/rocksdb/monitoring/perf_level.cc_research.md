# sources/storage-engines/rocksdb/monitoring/perf_level.cc

Purpose: Implements the thread-local perf instrumentation level API.

Important APIs/types/functions: Defines `thread_local PerfLevel perf_level = kEnableCount`, `SetPerfLevel(PerfLevel level)`, and `GetPerfLevel()`.

Control flow: `SetPerfLevel` asserts the supplied enum is between `kUninitialized` and `kOutOfBounds`, then stores it in thread-local state. Instrumentation macros and `PerfStepTimer` consult this level to decide whether to record counts, wall time, wait time, mutex time, or CPU time.

State and dependencies: State is per-thread and not persisted. Depends on `monitoring/perf_level_imp.h` and `<cassert>`.

Risks/test signals: Invalid levels are debug-asserted rather than returned as errors. Because the default is `kEnableCount`, timing metrics require callers to explicitly raise the level. Benchmarks do this before collecting detailed perf counters.
