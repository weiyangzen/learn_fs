<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedDBOptions.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedDBOptions.java

## Purpose

Managed DBOptions that tracks and closes a RocksDB Logger assigned through setLogger.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `ManagedDBOptions`. Notable methods: `setLogger`, `close`. Key imports include `static org.apache.hadoop.hdds.utils.db.managed.ManagedRocksObjectUtils.LOG`, `static org.apache.hadoop.hdds.utils.db.managed.ManagedRocksObjectUtils.track`, `java.util.concurrent.atomic.AtomicReference`, `org.apache.hadoop.hdds.utils.IOUtils`, `org.apache.ratis.util.UncheckedAutoCloseable`, `org.rocksdb.DBOptions`, `org.rocksdb.Logger`.

## Control flow

`setLogger` atomically swaps the logger and closes the previous one. `close` closes the current logger, then DBOptions, then leak tracker.

## State and persistence behavior

Holds an AtomicReference to the current Logger.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Only loggers set through this override are tracked. External logger sharing can cause premature close.

## Test signals

Set multiple loggers, assert previous/current close behavior, and verify leak metrics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedDBOptions.java -->
