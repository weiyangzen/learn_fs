# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/Notified.h

## Purpose
`Notified.h` provides a small monotonic value wrapper that lets actors wait until a numeric or metric-like value reaches a requested threshold. It is used for progress signals such as versions or time-like counters where waiters should complete as soon as the observed value advances far enough.

## Important APIs, Types, And Functions
- `IsMetricHandle<T>` detects `MetricHandle<T>` so metric-backed `Notified` instances can be initialized safely.
- `Notified<T, ValueType>` stores the current value and a priority queue of waiters keyed by threshold.
- `whenAtLeast(limit)` returns ready `Void()` if the value already meets the limit, otherwise enqueues a `Promise<Void>`.
- `set(v)` asserts monotonic increase, updates the value, pops all satisfied waiters, and sends them after removal.
- `initMetric(name, id)` initializes metric handles while preserving the current value.
- `NotifiedVersion` and `NotifiedDouble` are convenience aliases.

## Control Flow And State
The state is `val` plus a min-heap implemented by `std::priority_queue` with inverted comparison. `set()` moves promises out of the heap into a vector before sending them, which avoids callback reentrancy while the priority queue is being modified. Move construction and assignment transfer both value and waiter queue.

## Persistence And External State
The type is in-memory only. If `T` is a metric handle, `initMetric()` attaches it to TDMetric infrastructure; otherwise, invalid metric initialization emits a trace error. No data is serialized or persisted.

## Dependencies And Integration Points
It depends on `FDBTypes` for `Version`, Flow `Future`/`Promise`, TDMetric handles, Swift support annotations, and TraceEvent. It is a generic synchronization primitive for actor code and version notification patterns.

## Risks And Edge Cases
`set()` asserts `v >= val`; callers must never decrease values. `whenAtLeast()` can accumulate waiters indefinitely if the threshold is never reached. Metric initialization is compile-time gated but non-metric use logs an error instead of failing compilation. Moving an active `Notified` transfers pending waiters, so dangling references to the old object are unsafe.

## Test Signals
Tests should check immediate readiness, deferred readiness, multiple waiters released in threshold order, no release below limit, monotonic assertion behavior in debug builds, move semantics with pending waiters, and metric handle value preservation through `initMetric()`.
