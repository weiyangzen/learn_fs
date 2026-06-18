<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/slice.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/slice.cc

Purpose: Bridges Java `AbstractSlice`, heap `Slice`, and `DirectSlice` wrappers to C++ `ROCKSDB_NAMESPACE::Slice`.

Important APIs/types/functions: `createNewSliceFromString`, `Slice_createNewSlice0/1`, and `DirectSlice_createNewDirectSlice0/1` construct C++ slices. Shared operations include `size0`, `empty0`, `toString0`, `compare0`, `startsWith0`, and `disposeInternalJni`. Heap-slice operations expose `data0`, `clear0`, `removePrefix0`, and `disposeInternalBuf`. Direct-slice operations expose direct `ByteBuffer` creation, byte access, length mutation, clear/remove-prefix, and buffer disposal.

Control flow: Constructors allocate or reference backing memory, create a `Slice` pointing at it, and return the slice pointer. Data access copies slice bytes into Java arrays or returns a direct byte buffer. Prefix removal and clear mutate `Slice::data_`/`size_` behavior through RocksDB's public/private exposed members in this codebase.

State and persistence behavior: Slice state is in native memory and can either own a heap buffer allocated by the JNI bridge or reference Java direct-buffer memory. No RocksDB persistence occurs directly, but these slices are passed to DB range/property APIs elsewhere.

Dependencies and integration points: Depends on generated slice JNI headers, `rocksdb/slice.h`, pointer conversion, and `portal.h`. Many RocksJNI APIs consume the handles this file creates for ranges, SST writer keys, and suggested compaction ranges.

Risks: Buffer ownership is subtle. `createNewSliceFromString` allocates `len + 1` but constructs `Slice(buf)` relying on null termination. `clear0` and `disposeInternalBuf` compute the allocation base from `slice->data_ - internalBufferOffset`; mismatched offsets can free the wrong address. Direct slices depend on Java direct-buffer lifetime and support; non-direct buffers throw `IllegalArgumentException`. `DirectSlice_createNewDirectSlice1` uses `Slice(ptrData)` and therefore treats the direct buffer as null-terminated rather than using capacity.

Test signals: Tests should verify binary data with embedded zeros, offset disposal after `removePrefix`, direct and heap slice data round-trips, invalid non-direct buffer errors, compare/startsWith semantics, and leak/double-free behavior under sanitizers.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/slice.cc -->
