# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/SstFileManagerTest.java

## Purpose

This file checks basic Java wrapper behavior for `SstFileManager`, which tracks SST-file disk usage and deletion throttling.

## Important APIs and types

The suite uses `SstFileManager`, `Env.getDefault`, `setMaxAllowedSpaceUsage`, `isMaxAllowedSpaceReached`, `isMaxAllowedSpaceReachedIncludingCompactions`, `setCompactionBufferSize`, `getTotalSize`, `getTrackedFiles`, `getDeleteRateBytesPerSecond`, `setDeleteRateBytesPerSecond`, `getMaxTrashDBRatio`, and `setMaxTrashDBRatio`.

## Control flow

Each test constructs an `SstFileManager` in try-with-resources, reads default state or sets one property, then asserts the getter/derived status.

## State and persistence behavior

No DB is opened and no files are tracked, so state remains inside the native manager instance. Default size and tracked-file results should be empty or zero.

## Dependencies and integration points

The manager depends on `Env` and native RocksDB file-deletion accounting. These tests validate simple JNI property marshaling.

## Risks and test signals

Risks include broken constant values, wrong numeric conversion for long/double settings, and native handle leaks. Signals are exact defaults, setter round trips, and empty tracking maps.
