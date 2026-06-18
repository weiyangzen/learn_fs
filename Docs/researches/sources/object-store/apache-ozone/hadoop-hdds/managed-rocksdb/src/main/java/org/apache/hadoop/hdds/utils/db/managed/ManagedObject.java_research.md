<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedObject.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedObject.java

## Purpose

Package-private generic AutoCloseable wrapper for RocksDB AbstractNativeReference instances with leak tracking.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `ManagedObject`. Notable methods: `get`, `close`. Key imports include `static org.apache.hadoop.hdds.utils.db.managed.ManagedRocksObjectUtils.track`, `org.apache.ratis.util.UncheckedAutoCloseable`, `org.rocksdb.AbstractNativeReference`.

## Control flow

Construction stores the original object and registers with ManagedRocksObjectUtils.track. `get` exposes the underlying object. `close` closes the original in a try block and always closes the leak tracker.

## State and persistence behavior

Holds the native reference and its leak-tracker handle. It does not guard double-close beyond the wrapped RocksDB object's behavior.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Callers can still use `get()` after close, and duplicate close semantics depend on RocksDB classes. Every subclass must ensure close is called.

## Test signals

Use fake/real native references to verify original close, leak tracker closure, and no leak metrics after try-with-resources.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedObject.java -->
