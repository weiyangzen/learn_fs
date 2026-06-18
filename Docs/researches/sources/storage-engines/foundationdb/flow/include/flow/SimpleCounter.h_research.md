<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/SimpleCounter.h -->
# sources/storage-engines/foundationdb/flow/include/flow/SimpleCounter.h

Purpose: This header implements a lightweight global registry of process-lifetime counters for simple metric reporting. It supports `int64_t` and `double` counters that can be incremented from side threads.

Important APIs and types: `template <class T> class SimpleCounter` exposes `increment`, `get`, `name`, `makeCounter`, and `getCounters`. It specializes `increment` for `int64_t` using relaxed `fetch_add` and for `double` using a compare-exchange loop. `simpleCounterReport(Severity)` emits all counters.

Control flow: `makeCounter` allocates a counter, locks a static mutex, and appends it to a static registry vector. Increment updates the atomic value. `getCounters` returns a snapshot copy of the registry under the same mutex.

State and persistence behavior: Counters are intentionally process-lifetime heap allocations and are not meant to be freed. Counter values are in-memory atomics. Periodic reporting emits trace events but there is no durable counter file.

Dependencies and integration points: It depends on `Trace` for reporting severity and `Error` for Flow basics. It is used by low-overhead instrumentation where full TDMetric registration is unnecessary or too heavy.

Risks: Duplicate names create independent counters with the same display name. Registry entries leak by design. The double increment CAS loop uses default memory ordering and may spin under contention. There is no label support, so names must encode hierarchy and uniqueness.

Test signals: Tests should validate int and double increments, thread-safe registry insertion, duplicate name behavior, `getCounters` snapshots, and `simpleCounterReport` trace output formatting.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/SimpleCounter.h -->
