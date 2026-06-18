# sources/storage-engines/tikv/components/raft_log_engine/src/perf_context.rs

Purpose: Bridges raft-engine performance context counters into TiKV's `engine_traits::PerfContext` and `tracker` metrics.

Important APIs/types/functions: `RaftEnginePerfContext` implements `engine_traits::PerfContext`. `start_observe` resets raft-engine's current perf context with `raft_engine::set_perf_context(Default::default())`. `report_metrics(trackers)` reads `raft_engine::get_perf_context()` and writes derived nanosecond metrics into each `TrackerToken`.

Control flow: A caller starts observation, does raft-engine work, then reports metrics. For each tracker token, `GLOBAL_TRACKERS.with_tracker` updates `store_thread_wait_nanos`, `store_write_wal_nanos`, and `store_write_memtable_nanos`. WAL time sums log write, sync, and rotate durations; memtable time maps to raft-engine apply duration.

State and persistence behavior: This file only observes thread-local or process-local performance counters and writes in-memory tracker metrics. It persists nothing.

Dependencies and integration points: It depends on `raft_engine` perf context APIs, `engine_traits::PerfContext`, and TiKV `tracker`. `RaftLogEngine` returns this type from `PerfContextExt::get_perf_context`.

Risks: Metric field mapping is interpretive; if raft-engine perf context semantics change, tracker metrics could become misleading. Durations are cast from `u128` nanoseconds to `u64`, which is practically safe for normal intervals but technically lossy on extreme values.

Test signals: No local tests. Runtime observability and tracker-based tests are the likely validation path.
