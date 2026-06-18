<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/hadoop/hdds/utils/db/TestSstFileSetReader.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/hadoop/hdds/utils/db/TestSstFileSetReader.java

Purpose: Parameterized integration-style tests for reading and merging keys from multiple SST files with and without tombstone inclusion.

Important APIs/types/functions: Helpers create deterministic sorted SST files with alternating put/delete operation values and a long `KEY_PREFIX` containing all byte values modulo 256. `testGetKeyStream` validates regular RocksDB iterator output excludes tombstones. `testGetKeyStreamWithTombstone` validates raw native mode includes all keys. Overlap tests validate duplicate suppression and sorted order across multiple SSTs.

Control flow and state: `createDummyData` distributes a sorted key space round-robin over `numberOfFiles`, writes each file, then every sampled lower/upper bound pair is checked by filtering the original key map. Tests run for 0, 1, 2, 3, 7, and 10 files where applicable.

Dependencies and integration points: Exercises `SstFileSetReader`, `ManagedSstFileIterator`, native raw reader mode, `MinHeapMergeIterator`, `TestUtils.getTestingBounds`, and RocksDB SST writer wrappers.

Risks: Some comments say latest file precedence, but the key-only merge only guarantees one key per duplicate and sorted output, not value precedence. Native tombstone coverage is skipped when the native property/library is unavailable.

Test signals: Broad coverage of bounds, empty inputs, multiple file counts, tombstone inclusion/exclusion, large encoded keys, duplicate suppression, and sorted merge behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/hadoop/hdds/utils/db/TestSstFileSetReader.java -->
