<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedDirectSlice.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedDirectSlice.java

## Purpose

Defines `is` in package `org.apache.hadoop.hdds.utils.db.managed`.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `is`. Notable methods: `getNativeHandle`, `disposeInternal`. Key imports include `static org.apache.hadoop.hdds.utils.db.managed.ManagedRocksObjectUtils.track`, `java.nio.ByteBuffer`, `java.util.Objects`, `org.apache.ratis.util.UncheckedAutoCloseable`, `org.rocksdb.DirectSlice`.

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
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedDirectSlice.java -->
