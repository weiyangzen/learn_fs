## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/PerfContextTest.java

### Purpose

`PerfContextTest` validates Java access to RocksDB per-thread performance counters and string formatting.

### Important APIs, Types, And Functions

It uses `RocksDB.setPerfLevel`, `RocksDB.getPerfContext`, `PerfContext.reset`, JavaBeans `Introspector`, `PerfContext` getters, `getBlockReadCpuTime`, `getPostProcessTime`, and `PerfContext.toString`.

### Control Flow

Each test opens a DB with default and non-default CFs, sets a perf level that enables time and CPU counters, performs put/compact/get operations, retrieves the perf context, and asserts reset or getter behavior. The all-getters test reflects over bean properties to ensure every getter is linked and returns a `Long`.

### State And Persistence Behavior

The DB writes and compaction create enough native activity to populate counters. Perf context state is runtime per-thread diagnostic state, not persisted DB state.

### Dependencies And Integration Points

It integrates perf-level configuration, native perf context JNI getters, JavaBeans introspection, compaction, and platform assumptions. `getBlockReadCpuTime` is skipped on OpenBSD and Windows.

### Risks And Edge Cases

- Counter values can be platform-sensitive and workload-sensitive.
- Reflection can start testing new getters automatically when properties are added.
- CPU-time counters require OS support and correct perf-level selection.

### Test Signals

Signals are non-null context, all reflected getter results as `Long`, positive selected counters, and non-empty string output. Static research only; no test command was run.
