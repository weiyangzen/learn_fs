# sources/storage-engines/raft-engine/src/metrics.rs

Purpose: this file defines raft-engine's Prometheus metrics and a lightweight per-thread performance context. It gives the rest of the engine a uniform way to observe wall-clock durations either into Prometheus histograms, into thread-local cumulative counters, or both.

Important APIs and types: `StopWatch<M: TimeMetric>` records an `Instant` and observes elapsed time on drop. `PerfContext` stores cumulative durations for log population, write wait, file write, rotate, sync, and memtable apply. `get_perf_context`, `take_perf_context`, and `set_perf_context` manipulate the thread-local `TLS_PERF_CONTEXT`. `PerfContextField<P>` and the exported `perf_context!` macro create field projectors. `TimeMetric` abstracts `observe`/`observe_since`; implementations exist for `&Histogram`, `PerfContextField`, and `(M1, M2)`.

Control flow: operation sites create a `StopWatch` or call `observe_since`; the metric implementation either calls Prometheus `Histogram::observe` with seconds or mutates the projected duration inside the thread-local `PerfContext`. `take_perf_context` atomically replaces the current thread-local value with default and returns the old cumulative snapshot.

State and persistence behavior: all state is in process. Prometheus metric instances are global `lazy_static!` registries. `PerfContext` is thread-local and not synchronized across threads unless callers explicitly take or add contexts. `AddAssign<&PerfContext>` supports aggregating contexts into another context snapshot.

Dependencies and integration points: depends on `prometheus`, `prometheus_static_metric`, `lazy_static`, and `InstantExt` from `util.rs` to avoid negative elapsed durations. It exposes labeled metric vector wrappers for `LogQueueKind` and global histograms/gauges/counters used by write, read, purge, background rewrite, log-file accounting, swap-file accounting, log-entry accounting, and memory usage.

Risks and invariants: histogram registration unwraps at initialization, so duplicate names or registration failure panic early. `PerfContextField` uses `RefMut::map` inside TLS and assumes no nested incompatible borrow of the same thread-local context. `StopWatch` observes on drop, so long-lived scopes or early drops affect measured spans. Metrics are process-global, which is expected for Prometheus but makes tests sensitive to global registration reuse.

Test signals: no direct tests in this file. It is indirectly exercised by engine write/read/purge code, by `StopWatch` use in purge and write paths, and by memory/swap metric updates in memtable and swappy allocator.
