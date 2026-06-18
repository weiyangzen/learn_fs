# sources/storage-engines/rocksdb/monitoring/iostats_context.cc

Purpose: Implements thread-local IO statistics context access, reset behavior, and string formatting.

Important APIs/types/functions: Defines `thread_local IOStatsContext iostats_context` unless `NIOSTATS_CONTEXT` is set, `get_iostats_context()`, `IOStatsContext::Reset`, and `IOStatsContext::ToString`.

Control flow: `Reset` zeroes byte counters, IO timing counters, CPU timing counters, resets temperature-specific file IO stats, and sets `thread_pool_id` to `Env::Priority::TOTAL`. `ToString` uses a macro to emit all counters or only non-zero counters, then trims trailing comma/space.

State and persistence behavior: IO stats are thread-local and in-memory. With `NIOSTATS_CONTEXT`, a dummy static context exists only to keep API shape simple; reset/string operations become no-ops or empty output.

Dependencies/integration: Depends on `monitoring/iostats_context_imp.h`, `rocksdb/env.h`, and public `rocksdb/iostats_context.h`. Instrumented Env/file code updates these counters through macros in the imp header.

Risks/test signals: Counters are not thread-safe by design because each thread has its own context. Formatting relies on trimming `find_last_not_of(", ")`; tests cover zero-included and zero-excluded strings.
