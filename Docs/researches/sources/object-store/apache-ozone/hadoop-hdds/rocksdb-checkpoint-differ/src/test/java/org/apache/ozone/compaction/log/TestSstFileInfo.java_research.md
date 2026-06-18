<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/ozone/compaction/log/TestSstFileInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/ozone/compaction/log/TestSstFileInfo.java

Purpose: Unit test for constructing `SstFileInfo` from RocksDB `LiveFileMetaData`.

Important APIs/types/functions: The test mocks `LiveFileMetaData.fileName`, `columnFamilyName`, `smallestKey`, and `largestKey`, builds an expected `SstFileInfo`, and compares it to `new SstFileInfo(lfm)`.

Control flow and state: No persistent state. Mockito supplies byte arrays through `StringUtils.string2Bytes`; the constructor under test decodes them and strips the `.sst` basename from `/1.sst` to `1`.

Dependencies and integration points: Verifies the metadata conversion used by `RdbUtil`, `CompactionFileInfo.Builder.setValues`, and compaction listener file-info generation.

Risks: Only one happy path is covered. It does not cover null metadata, binary/non-UTF key bytes, or paths with unusual names.

Test signals: Confirms file-name basename extraction and string decoding of RocksDB metadata fields.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/test/java/org/apache/ozone/compaction/log/TestSstFileInfo.java -->
