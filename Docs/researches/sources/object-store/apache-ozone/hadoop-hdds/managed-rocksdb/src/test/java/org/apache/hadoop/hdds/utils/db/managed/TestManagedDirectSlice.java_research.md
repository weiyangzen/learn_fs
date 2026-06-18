<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/test/java/org/apache/hadoop/hdds/utils/db/managed/TestManagedDirectSlice.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/test/java/org/apache/hadoop/hdds/utils/db/managed/TestManagedDirectSlice.java

## Purpose

JUnit test suite for ManagedDirectSlice ByteBuffer slicing semantics.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `TestManagedDirectSlice`. Notable methods: `testManagedDirectSlice`. Key imports include `static org.junit.jupiter.api.Assertions.assertEquals`, `java.nio.ByteBuffer`, `java.util.Random`, `org.apache.hadoop.hdds.utils.db.CodecBuffer`, `org.junit.jupiter.api.Test`.

## Control flow

Loads RocksDB native library once, then tests many sizes and buffer positions by comparing ManagedDirectSlice against a ManagedSlice built from the expected bytes.

## State and persistence behavior

Uses static Random and count for generated cases and logging. It creates only temporary direct buffers/native slices inside try-with-resources.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Randomized sizes improve coverage but make exact failing cases less reproducible unless the printed count/size/position is captured.

## Test signals

This file is itself the test signal for direct slice offset, size, equality, and close behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/test/java/org/apache/hadoop/hdds/utils/db/managed/TestManagedDirectSlice.java -->
