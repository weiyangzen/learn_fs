<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/hadoop/hdds/utils/db/RDBSstFileWriter.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/hadoop/hdds/utils/db/RDBSstFileWriter.java

Purpose: Closeable wrapper around RocksDB's `SstFileWriter` for writing new SST files from byte arrays or `CodecBuffer` instances, including tombstone entries.

Important APIs/types/functions: The constructor opens a new managed SST writer for a target `File`. Public methods are `put(byte[], byte[])`, `put(CodecBuffer, CodecBuffer)`, `delete(byte[])`, `delete(CodecBuffer)`, and `close()`. `keyCounter` tracks whether `finish()` should be called. `closeOnFailure` closes native resources when RocksDB operations fail.

Control flow and state: Each successful put/delete increments `keyCounter`. `close` calls `finish()` only for non-empty files because RocksDB rejects finishing empty SSTs, then closes writer/options/env options and resets the counter. CodecBuffer deletes wrap the key in `ManagedDirectSlice`.

Dependencies and integration points: Used by `RocksDBCheckpointDiffer.removeValueFromSSTFile` to rewrite backed-up SSTs with keys and empty values or tombstones while pruning OMKeyInfo payloads. Depends on managed RocksDB native wrappers and `RocksDatabaseException`.

Risks: Writer order requirements are inherited from RocksDB; callers must write sorted keys. The class is single-use after close because resources are nulled/closed. Exceptions during close are propagated as `RocksDatabaseException`.

Test signals: `TestRDBSstFileWriter` exercises CodecBuffer reuse, put/delete tombstone creation, empty value writing, native raw readback, and file existence.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/hadoop/hdds/utils/db/RDBSstFileWriter.java -->
