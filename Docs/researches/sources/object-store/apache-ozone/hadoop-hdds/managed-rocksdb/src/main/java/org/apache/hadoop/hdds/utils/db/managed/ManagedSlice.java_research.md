<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedSlice.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedSlice.java

## Purpose

Managed Slice wrapper that tracks RocksDB native slice resources; ManagedDirectSlice builds a DirectSlice over the remaining region of a ByteBuffer slice.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `ManagedSlice`. Notable methods: `getNativeHandle`, `disposeInternal`. Key imports include `static org.apache.hadoop.hdds.utils.db.managed.ManagedRocksObjectUtils.track`, `org.apache.ratis.util.UncheckedAutoCloseable`, `org.rocksdb.Slice`.

## Control flow

Constructors pass byte data or a sliced ByteBuffer to RocksDB. Because RocksMutableObject.close is final, disposeInternal is decorated to close the leak tracker after native disposal.

## State and persistence behavior

Owns native slice memory/reference and exposes synchronized getNativeHandle for JNI consumers.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

ByteBuffer position/limit semantics are critical for ManagedDirectSlice. Using non-direct or mutated buffers can cause unexpected slice contents.

## Test signals

The included ManagedDirectSlice test compares direct slices across sizes and offsets; add tests for empty, non-direct, and lifecycle behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedSlice.java -->
