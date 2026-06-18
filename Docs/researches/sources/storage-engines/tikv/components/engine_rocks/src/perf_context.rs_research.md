<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/perf_context.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/perf_context.rs

Purpose: exposes RocksDB perf-context collection through the engine abstraction.

Important APIs/types/functions: `PerfContextExt for RocksEngine`, `RocksPerfContext`, `RocksPerfContext::new`, and `PerfContext` trait methods `start_observe` and `report_metrics`.

Control flow: callers construct a context for a `PerfLevel` and `PerfContextKind`, call `start_observe` to reset/apply perf settings, then call `report_metrics` with tracker tokens to report captured counters through `PerfContextStatistics`.

State and persistence behavior: operates on RocksDB thread-local perf context and tracker metrics only; no DB data is persisted or modified.

Dependencies/integration: thin facade over `perf_context_impl::PerfContextStatistics`, used by storage, coprocessor, and raftstore request paths.

Risks: metrics are only meaningful if start/report bracket the correct work on the same thread. Disabled perf level makes collection a no-op.

Test signals: implementation logic is tested in `perf_context_impl.rs` field operation tests; runtime correctness is integration-level.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/perf_context.rs -->
