# sources/storage-engines/tikv/components/engine_panic/src/perf_context.rs

Purpose: Panic skeleton for engine performance context collection.

Important APIs and types: `PanicEngine` implements `PerfContextExt` with associated `PanicPerfContext`. `PanicPerfContext` implements `start_observe` and `report_metrics`.

Control flow and state: All methods panic. There is no performance counter state.

Dependencies and integration: Uses `PerfLevel`, `PerfContextKind`, and `tracker::TrackerToken`. Real engines use this for RocksDB perf-context reporting.

Risks: Runtime use panics.

Test signals: No tests.
