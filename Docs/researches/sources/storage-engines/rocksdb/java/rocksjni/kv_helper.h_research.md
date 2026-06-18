<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/kv_helper.h -->
# sources/storage-engines/rocksdb/java/rocksjni/kv_helper.h

## Purpose
Defines RAII-style helpers for byte-array and direct-buffer key/value transfer plus a `KVException` helper for throwing Java exceptions from low-level buffer code.

## Important APIs and Types
Key/value JNI helper classes. This file's Java-native surface is centered on the RocksJNI generated `Java_org_rocksdb_*` entry points or the declared callback/helper type named above. It follows the repository convention of passing native pointers through Java `long` handles and using `portal.h`/converter helpers for Java object construction and exception mapping.

## Control Flow
`JByteArraySlice` and `JDirectBufferSlice` expose Java key memory as RocksDB `Slice`s. `JByteArrayPinnableSlice` and `JDirectBufferPinnableSlice` copy native `PinnableSlice` values into Java byte arrays or direct buffers, returning full native lengths and handling partial copies. `KVException` centralizes throwing RocksDB or argument exceptions.

## State and Persistence Behavior
State is per-call pinned/copy buffers and `PinnableSlice` storage. It is transient and must not outlive JNI local references or Java buffers.

## Dependencies and Integration Points
Depends on `portal.h`, `Slice`, `PinnableSlice`, and JNI array/direct-buffer APIs. Risks include forgetting to release pinned byte arrays, direct buffer null/address validation, buffer truncation semantics, and exception paths in destructors/cleanup. Tests should cover gets into arrays/direct buffers, small buffers, and invalid offsets/lengths.

## Risks and Test Signals
Risk review should include JNI ownership, null or stale handles, Java/native enum or signature drift, and exception paths where JNI can leave a pending exception. Useful tests are Java API round trips, native-handle disposal order, RocksDB integration tests that exercise the option/callback in a live DB, and sanitizer/leak runs for repeated construction and disposal.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/kv_helper.h -->
