<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/hadoop/hdds/utils/db/TestRDBSstFileWriter.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/hadoop/hdds/utils/db/TestRDBSstFileWriter.java

Purpose: Native-only test for writing SST entries from reusable `CodecBuffer` instances and reading back tombstone/value entries.

Important APIs/types/functions: `testSstFileTombstoneCreationWithCodecBufferReuse` loads the raw SST native library, opens `RDBSstFileWriter`, uses a `CodecBuffer` fed by a `PutToByteBuffer` lambda, writes alternating delete and put entries, then reads the SST with `ManagedRawSSTFileReader`.

Control flow and state: The test verifies buffer readable length and content before/after clearing, writes keys in sorted order expected by RocksDB, closes the writer, checks file existence, then iterates raw key/value records and validates operation type and empty value bytes.

Dependencies and integration points: Covers the writer path used by `RocksDBCheckpointDiffer.removeValueFromSSTFile` during key-only SST rewriting.

Risks: Enabled only when native RocksDB tooling is available. The assertion comparing `keys.get(idx)` to itself appears ineffective for validating read key content, so operation type and empty value checks carry most of the signal.

Test signals: Confirms writer close produces a file, CodecBuffer reuse does not corrupt written entries, raw iterator sees tombstone/value operation types, and empty values are preserved.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/hadoop/hdds/utils/db/TestRDBSstFileWriter.java -->
