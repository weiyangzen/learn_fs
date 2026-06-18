## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MutableOptionsGetSetTest.java

### Purpose

`MutableOptionsGetSetTest` validates round trips between Java mutable option builders and RocksDB native state through `createColumnFamily`, `setOptions`, `getOptions`, `setDBOptions`, and `getDBOptions`.

### Important APIs, Types, And Functions

Covered APIs include `ColumnFamilyOptions` setters for blob, memtable, compaction, and report options; `MutableColumnFamilyOptions.builder`; `RocksDB.setOptions` with and without CF handle; `RocksDB.getOptions`; `MutableDBOptions.builder`; `RocksDB.setDBOptions`; and `RocksDB.getDBOptions`.

### Control Flow

The first test creates two CFs with different `ColumnFamilyOptions` and asserts `getOptions(handle)` returns each configured value. The second creates CFs with default options, flushes, applies mutable CF options through `setOptions(handle, ...)`, then reads them back. The third applies mutable CF options to the default CF with `setOptions(...)`. The last applies mutable DB options and verifies live DB option values.

### State And Persistence Behavior

This file exercises live mutable native configuration. CF option changes affect per-CF runtime state; DB option changes affect DB-wide runtime state such as background jobs, WAL size, sync bytes, stats periods, and file buffer sizes. Data persistence is not the focus, but DB handles and CF handles must remain valid through native option updates.

### Dependencies And Integration Points

It integrates Java option builders with native RocksDB option mutation APIs, blob files, compaction thresholds, memtable behavior, and DB-level runtime controls.

### Risks And Edge Cases

- Some C++ constraints normalize values; comments call out ratio constraints, so exact assertions are sensitive to native option validation.
- Mutable and immutable options are easy to mix; only mutable fields should be accepted by `setOptions`.
- Blob-related options span feature enablement and GC thresholds, so partial round-trip failures can hide until blob DB behavior is used.

### Test Signals

Signals are exact `getOptions` and `getDBOptions` values after create or set, including two CFs with intentionally different values. Static research only; no test command was run.
