# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/PerfContext.java research

## Purpose

`PerfContext` is the Java wrapper for RocksDB's per-thread performance counters. It exposes counters and timings for reads, writes, cache activity, iterators, blob reads, environment operations, transaction locks, encryption, CPU time, and async seek behavior.

## Important APIs and types

The protected constructor wraps a native handle. `reset()` clears counters. Dozens of getters call native methods and return `long` counters or nanosecond timings. `toString()` delegates to `toString(true)`, while `toString(boolean excludeZeroCounters)` asks native code for a formatted summary. `disposeInternal()` intentionally does nothing because the perf context is valid for the application lifetime.

## Control flow

Java code obtains a `PerfContext` from higher-level RocksDB APIs, performs DB operations with perf collection enabled through `PerfLevel`, then reads counters or calls `toString`. Every getter is a direct JNI call into the native context.

## State and persistence behavior

State lives in native thread-local or process-managed perf context memory. It is transient diagnostic state and does not persist to DB files. `reset()` affects only the active context counters.

## Dependencies and integration points

It depends on `RocksObject` for handle storage but bypasses normal disposal. It integrates with `PerfLevel`, DB read/write/iterator paths, block cache, blob cache, secondary cache, memtables, Env wrappers such as timed or encrypted envs, and transaction lock managers.

## Risks and test signals

Risks include counters requiring the correct `PerfLevel`, thread-local interpretation, stale data if not reset, and native method drift as counters are added or renamed. Tests should enable each relevant perf level, reset before controlled operations, assert non-zero expected counters for gets/iterators/writes/cache hits, verify `excludeZeroCounters`, and ensure close/dispose is harmless.
