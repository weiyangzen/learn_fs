<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedRocksDB.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedRocksDB.java

## Purpose

Managed wrapper around RocksDB with factory methods for open/openReadOnly/openWithLatestOptions, synchronized live-file deletion, and live SST metadata lookup.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `ManagedRocksDB`. Notable methods: `openReadOnly`, `openReadOnly`, `openReadOnly`, `open`, `openWithLatestOptions`, `deleteFile`, `getLiveMetadataForSSTFiles`, `getLiveMetadataForSSTFiles`. Key imports include `java.io.File`, `java.time.Duration`, `java.util.List`, `java.util.Map`, `java.util.stream.Collectors`, `org.apache.commons.io.FilenameUtils`, `org.apache.hadoop.hdds.utils.db.RocksDatabaseException`, `org.rocksdb.ColumnFamilyDescriptor`, `org.rocksdb.ColumnFamilyHandle`, `org.rocksdb.DBOptions`.

## Control flow

Static open methods delegate to RocksDB APIs and wrap the result. `openWithLatestOptions` first loads persisted options into supplied DB/CF descriptors. `deleteFile` calls RocksDB.deleteFile and waits up to 60 seconds for the file to disappear.

## State and persistence behavior

Owns a RocksDB native handle through ManagedObject. Column family handles passed to open methods remain caller-owned.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Callers must close DB and all column-family handles. `deleteFile` relies on filesystem deletion timing and can block; live-file maps key by basename, which can collide if paths differ.

## Test signals

Open temp DBs with multiple column families, verify latest-options loading, delete live files under compaction-safe conditions, and assert close/leak metrics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedRocksDB.java -->
