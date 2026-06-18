<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdb/util/RdbUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdb/util/RdbUtil.java

Purpose: Utility methods for collecting live RocksDB SST metadata by column family, primarily for snapshot-diff comparison support.

Important APIs/types/functions: `getLiveSSTFilesForCFs(ManagedRocksDB, Set<String>)` filters RocksDB live file metadata by column family. `getSSTFilesForComparison` maps those entries to `SstFileInfo` set values. `getSSTFilesWithInodesForComparison` maps filesystem inode values to `SstFileInfo` using `IOUtils.getINode`.

Control flow and state: The class is stateless. Each method calls RocksDB live metadata at invocation time, filters by decoded column-family name, and builds fresh collections.

Dependencies and integration points: Depends on `ManagedRocksDB`, RocksDB `LiveFileMetaData`, HDDS string conversion, filesystem inode lookup, and `SstFileInfo`. It can be used to compare snapshot hard links or live SST identities.

Risks: The class comment says it is temporary. Inode-based comparison depends on filesystem support and can throw `IOException`. Live metadata is a point-in-time view and can race with RocksDB compaction unless callers coordinate.

Test signals: `TestSstFileInfo` validates `SstFileInfo` construction from mocked live metadata; broader integration should test live DB metadata and inode behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/rocksdb-checkpoint-differ/src/main/java/org/apache/ozone/rocksdb/util/RdbUtil.java -->
