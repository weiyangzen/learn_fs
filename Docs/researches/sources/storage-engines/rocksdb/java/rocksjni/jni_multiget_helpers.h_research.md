<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/jni_multiget_helpers.h -->
# sources/storage-engines/rocksdb/java/rocksjni/jni_multiget_helpers.h

## Purpose
Declares helper classes `MultiGetJNIKeys`, `MultiGetJNIValues`, and `ColumnFamilyJNIHelpers` for Java MultiGet implementations.

## Important APIs and Types
MultiGet JNI helper declarations. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
The key helper owns arrays/vectors and exposes `data()`/`size()` for RocksDB calls. The value helper declares byte-array and byte-buffer materialization APIs. Column-family helpers declare conversion from `jlongArray` and single handles into native pointer vectors or status errors.

## State and Persistence Behavior
The classes manage per-call transient memory only. Correct lifetime is crucial because `Slice` entries reference storage owned by the helper.

## Dependencies and Integration Points
Integration is with RocksDB Java DB MultiGet JNI files. Risks are accidental copying/moving that invalidates slice pointers, count mismatches, and status-vector ownership confusion. Tests should include compile coverage plus MultiGet behavior with varying key counts and CF handles.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/jni_multiget_helpers.h -->
