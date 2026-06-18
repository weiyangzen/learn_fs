# sources/storage-engines/rocksdb/monitoring/perf_level_imp.h

Purpose: Declares the internal thread-local `perf_level` variable used by perf-context macros.

Important APIs/types/functions: `extern thread_local PerfLevel perf_level`.

Control flow/integration: Included by `perf_step_timer.h`, `perf_context_imp.h`, and `perf_level.cc`; consumers compare the current value with required enable levels before recording measurements.

State and dependencies: No implementation state in this header beyond the external declaration. Depends on `port/port.h` and public `rocksdb/perf_level.h`.

Risks/test signals: It is a narrow glue header; correctness depends on exactly one definition in `perf_level.cc` and consistent thread-local support on the target platform.
