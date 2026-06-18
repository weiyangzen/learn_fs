# sources/storage-engines/tikv/components/engine_traits/src/perf_context.rs

Purpose: Abstracts backend performance-context metrics collection.

Important APIs and control flow: `PerfLevel` enumerates measurement levels and has numeric serialization support. `PerfContextExt` creates a backend `PerfContext` for a level and subsystem `PerfContextKind`. `PerfContextKind` identifies raftstore apply/store, storage commands, or coprocessor requests. `PerfContext` starts observation and reports collected metrics to Prometheus/trackers.

State, persistence, and dependencies: Perf contexts hold transient measurement counters, often backed by backend thread-local/global state. Dependencies include `tikv_util::numeric_enum_serializing_mod` and `tracker::TrackerToken`.

Integration points, risks, and test signals: Used by storage, raftstore, and coprocessor observability. Risks include global-vs-per-engine ambiguity, no-op alternate engines hiding regressions, level serialization drift, and forgotten `start_observe`. Signals are metrics tests and runtime Prometheus/tracker observations.
