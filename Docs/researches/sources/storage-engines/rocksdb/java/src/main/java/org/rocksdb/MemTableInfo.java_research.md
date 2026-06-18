# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/MemTableInfo.java research

## Purpose

`MemTableInfo` is an immutable Java metadata object describing one memtable: its column family, sequence-number range signals, entry count, and delete count.

## Important APIs and types

The package-private constructor is intended for JNI and tests. Accessors expose `columnFamilyName`, `firstSeqno`, `earliestSeqno`, `numEntries`, and `numDeletes`. `equals()`, `hashCode()`, and `toString()` make it suitable for assertions and diagnostics.

## Control flow

Native code or tests construct instances. Java callers read fields or compare objects. No refresh or native calls occur after construction.

## State and persistence behavior

The class is a point-in-time metadata snapshot. It describes in-memory memtable state, not durable SST state. Sequence-number fields help reason about what writes may be present in this memtable or later memtables.

## Dependencies and integration points

It depends on `java.util.Objects` and integrates with RocksDB metadata APIs that expose memtable state to Java.

## Risks and test signals

Metadata can become stale quickly as writes and flushes proceed. Tests should verify equality semantics, string output for diagnostics, JNI construction, and sequence/entry counts after controlled writes and deletes.
