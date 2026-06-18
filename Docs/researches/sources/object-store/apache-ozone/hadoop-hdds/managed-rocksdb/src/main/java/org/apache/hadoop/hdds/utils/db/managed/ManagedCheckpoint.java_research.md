<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedCheckpoint.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedCheckpoint.java

## Purpose

Managed wrapper around RocksDB `Checkpoint` that adds close-time leak tracking to a native RocksDB resource.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `ManagedCheckpoint`. Notable methods: `create`. Key imports include `org.rocksdb.Checkpoint`.

## Control flow

The class constructs or inherits the RocksDB object, registers a leak tracker at construction, and overrides close or wrapping methods so the native resource closes before the tracker is released.

## State and persistence behavior

Owns a RocksDB native handle and a leak-tracker token. It has no durable state.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Safety depends on try-with-resources by callers and on RocksDB ownership semantics remaining stable across rocksdbjni upgrades.

## Test signals

Use try-with-resources in representative RocksDB operations and assert ManagedRocksObjectMetrics reports no leaks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedCheckpoint.java -->
