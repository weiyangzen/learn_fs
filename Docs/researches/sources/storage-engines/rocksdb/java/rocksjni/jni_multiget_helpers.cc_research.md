<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/jni_multiget_helpers.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/jni_multiget_helpers.cc

## Purpose
Implements reusable helpers for RocksDB Java MultiGet paths: key extraction, value/status materialization, and column-family handle validation.

## Important APIs and Types
MultiGet JNI helper implementation. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
`MultiGetJNIKeys` builds vectors of `Slice` and backing storage from Java byte arrays or byte buffers. `MultiGetJNIValues::byteArrays` turns `PinnableSlice` results into Java 2D arrays with per-key status handling. `fillByteBuffersAndStatusObjects` copies into direct buffers, marks incomplete when buffers are too small, and fills Java status objects. `ColumnFamilyJNIHelpers` validates handle arrays and single handles.

## State and Persistence Behavior
State is per-call stack/heap vectors retaining key backing memory until the RocksDB call completes. It does not persist, but handles pinned values and statuses from reads.

## Dependencies and Integration Points
Depends on `JniUtil`, `StatusJni`, `ByteJni`, and RocksDB `PinnableSlice`. Risks include local ref pressure for large batches, direct buffer capacity truncation, mismatched CF/key counts, and keeping slices beyond backing storage lifetime. Tests should cover byte-array and direct-buffer MultiGet, partial buffers, null CF arrays, and non-OK statuses.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/jni_multiget_helpers.cc -->
