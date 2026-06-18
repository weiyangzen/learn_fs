<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/test/java/org/apache/hadoop/hdds/utils/db/managed/TrackingUtilManagedWriteBatchForTesting.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/test/java/org/apache/hadoop/hdds/utils/db/managed/TrackingUtilManagedWriteBatchForTesting.java

## Purpose

Defines `extends` in package `org.apache.hadoop.hdds.utils.db.managed`.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `extends`. Notable methods: `equals`, `hashCode`, `toString`, `getOperations`, `convert`, `delete`, `delete`, `delete`, `delete`, `deleteRange`, `deleteRange`, `merge`, `merge`, `put`, `put`, `put`, `put`, `close`. Key imports include `static org.apache.hadoop.hdds.StringUtils.bytes2String`, `java.nio.ByteBuffer`, `java.util.ArrayList`, `java.util.Arrays`, `java.util.HashMap`, `java.util.List`, `java.util.Map`, `org.rocksdb.ColumnFamilyHandle`, `org.rocksdb.RocksDBException`.

## Control flow

Control flow is limited to the methods listed below.

## State and persistence behavior

State follows the fields declared in the class.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Review call sites for lifecycle and concurrency assumptions.

## Test signals

Compile and targeted unit tests should cover normal and exceptional paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/test/java/org/apache/hadoop/hdds/utils/db/managed/TrackingUtilManagedWriteBatchForTesting.java -->
