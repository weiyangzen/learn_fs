# sources/storage-engines/rocksdb/monitoring/perf_context_imp.h

Purpose: Internal header defining perf-context globals and instrumentation macros used throughout RocksDB hot paths.

Important APIs/types/functions: Declares the current `PerfContext` object, with Solaris indirection and `NPERF_CONTEXT` disabled mode. Macros include timer start/stop/guard variants, CPU timer guards, conditional mutex timer guards, wait timer guards, measurement, and counter increment macros including per-level increments.

Control flow: In enabled builds, timer macros create `PerfStepTimer` stack objects and start them immediately or conditionally. Counter macros check `perf_level >= kEnableCount` before mutating fields. Per-level increments lazily create a `PerfContextByLevel` entry for the supplied level when per-level tracking is enabled.

State/dependencies: Mutates thread-local `perf_context` and reads thread-local `perf_level`. Depends on `perf_step_timer.h`, public `rocksdb/perf_context.h`, and stop-watch utilities.

Risks/test signals: Macro-based instrumentation has scope/name constraints and assumes the metric field exists. Disabled builds compile macros to no-ops, so code must not depend on side effects inside macro arguments except for the explicit clock cast in CPU guards.
