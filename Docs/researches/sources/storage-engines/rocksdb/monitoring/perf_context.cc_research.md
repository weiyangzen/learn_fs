# sources/storage-engines/rocksdb/monitoring/perf_context.cc

Purpose: Implements RocksDB's per-thread performance context storage, reset/copy/string formatting, and optional per-level read metrics.

Important APIs/types/functions: Large macros `DEF_PERF_CONTEXT_METRICS` and `DEF_PERF_CONTEXT_LEVEL_METRICS` enumerate all fields that must match public `PerfContextBase` and `PerfContextByLevelBase`. `get_perf_context()` returns the thread-local/global context and performs static layout/offset validation. `PerfContext::Reset`, `copyMetrics`, `ToString`, `EnablePerLevelPerfContext`, `DisablePerLevelPerfContext`, and `ClearPerLevelPerfContext` manage metrics.

Control flow: On access, compile-time static assertions ensure internal macro-generated structs have the same size and offsets as public headers. Reset zeros all declared metrics and optionally per-level maps. ToString emits counters, optionally skipping zeros, and appends per-level values as `value@levelN`.

State and dependencies: Normally `thread_local PerfContext perf_context` holds per-thread counters; `NPERF_CONTEXT` builds use a dummy global. Per-level data is heap-allocated as `std::map<uint32_t, PerfContextByLevel>`. Depends on `monitoring/perf_context_imp.h`.

Risks/test signals: Adding a public perf metric requires updating the macros or static assertions fail. Copying can allocate a per-level map; destructor clears it outside Solaris/non-disabled builds. Formatting trims trailing separators. Benchmarks in `db_basic_bench.cc` exercise selected counters.
