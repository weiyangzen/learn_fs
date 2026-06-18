<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedRocksObjectUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedRocksObjectUtils.java

## Purpose

Central utility for RocksDB wrapper leak tracking, leak reporting, RocksDB native library loading, RocksDB JNI library-name lookup, and polling for file deletion.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `ManagedRocksObjectUtils`. Notable methods: `waitForFileDelete`, `loadRocksDBLibrary`, `getRocksDBLibFileName`. Key imports include `jakarta.annotation.Nullable`, `java.io.File`, `java.time.Duration`, `org.apache.hadoop.hdds.HddsUtils`, `org.apache.hadoop.hdds.ratis.RatisHelper`, `org.apache.hadoop.hdds.utils.LeakDetector`, `org.apache.hadoop.hdds.utils.db.RocksDatabaseException`, `org.apache.ratis.util.UncheckedAutoCloseable`, `org.rocksdb.RocksDB`, `org.rocksdb.util.Environment`.

## Control flow

`track` registers a closeable with LeakDetector and captures a shortened stack trace. `waitForFileDelete` polls through RatisHelper until a path disappears. `loadRocksDBLibrary` delegates to RocksDB.loadLibrary.

## State and persistence behavior

Holds a static LeakDetector and uses process-wide metrics. It does not persist runtime state.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Stack capture depends on logging configuration. File deletion polling can make tests slow or flaky on busy filesystems.

## Test signals

Exercise tracking/reportLeak counters, file-delete timeout and success paths, and RocksDB library-name resolution on supported platforms.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedRocksObjectUtils.java -->
