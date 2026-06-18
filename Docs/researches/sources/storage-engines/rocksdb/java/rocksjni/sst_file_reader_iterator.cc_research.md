<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/sst_file_reader_iterator.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/sst_file_reader_iterator.cc

Purpose: Provides Java access to `ROCKSDB_NAMESPACE::Iterator` instances returned by `SstFileReader`.

Important APIs/types/functions: Methods wrap iterator lifecycle (`disposeInternalJni`), movement (`isValid0Jni`, `seekToFirst0Jni`, `seekToLast0Jni`, `next0Jni`, `prev0Jni`), seeking (`seek0Jni`, `seekForPrev0Jni`, direct and byte-array seek variants), status checking, key/value retrieval as arrays, direct-buffer copies, byte-array buffer copies, and `Refresh` with or without a snapshot.

Control flow: Java methods pass the iterator handle. Seek methods convert Java key data into temporary `Slice`s and call `Seek`/`SeekForPrev`. Key/value methods read `it->key()` or `it->value()` and either allocate arrays or copy into caller buffers, returning the full required length for buffer APIs. `status0Jni` and refresh methods translate non-OK statuses into exceptions.

State and persistence behavior: Iterator position and status live in the native iterator. No persistent data is changed. Snapshot refresh can bind the iterator to a supplied snapshot view.

Dependencies and integration points: Includes generated `org_rocksdb_SstFileReaderIterator.h`, `rocksdb/iterator.h`, and `portal.h`. Created by `sst_file_readerjni.cc` and consumed by Java SST inspection APIs.

Risks: Methods assume `Valid()` before key/value access; invalid iterator access is undefined by RocksDB contract. The OOM branches after `new char[jtarget_len]` are ineffective with throwing `new`. The `FindClass` string for OOM is `"/lang/java/OutOfMemoryError"`, which looks malformed. Byte-array copy methods rely on Java to provide valid offsets and do not explicitly check exceptions after `SetByteArrayRegion`.

Test signals: Tests should iterate an SST forward/backward, seek using arrays/direct/byte-buffer paths, verify truncation return lengths, check `status()` after corruption or bad reads, refresh with snapshots, and exercise invalid/non-direct buffers.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/sst_file_reader_iterator.cc -->
