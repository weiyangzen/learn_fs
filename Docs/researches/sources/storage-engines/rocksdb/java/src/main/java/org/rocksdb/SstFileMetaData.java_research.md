# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/SstFileMetaData.java

## Purpose
`SstFileMetaData` is an immutable Java data transfer object describing one SST file as reported by native RocksDB metadata APIs. It captures identity, path, file size, key range, sequence number range, read/compaction state, entry/deletion counts, and optional full-file checksum bytes.

## Important APIs and Types
The protected constructor is intended for JNI construction and stores all supplied values directly. Public accessors include `fileName()`, `path()`, `size()`, `smallestSeqno()`, `largestSeqno()`, `smallestKey()`, `largestKey()`, `numReadsSampled()`, `beingCompacted()`, `numEntries()`, `numDeletions()`, and `fileChecksum()`.

## Control Flow
There is no active control flow beyond construction and simple field access. Native code creates instances with already-collected metadata; Java callers consume the read-only getters.

## State and Persistence Behavior
The object mirrors persistent SST-file metadata but does not persist anything itself. `byte[]` fields are stored and returned directly, so Java callers can mutate arrays that conceptually represent immutable metadata.

## Dependencies and Integration Points
The class integrates with RocksDB JNI metadata conversion, typically from DB/file property APIs that enumerate live files. It has no superclass and no direct native methods.

## Risks and Test Signals
Tests should verify JNI field ordering, optional checksum behavior, null/empty key handling, and that read state such as `beingCompacted` and read-sampling count reflects native metadata. The main risk is aliasing of `byte[]` fields because defensive copies are intentionally omitted.
