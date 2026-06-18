<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/sst_file_readerjni.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/sst_file_readerjni.cc

Purpose: Bridges Java `SstFileReader` to C++ `ROCKSDB_NAMESPACE::SstFileReader` for offline SST file inspection.

Important APIs/types/functions: `newSstFileReader` constructs from `Options`. `open` opens a file path and throws on non-OK `Status`. `newIterator` returns an iterator for supplied `ReadOptions`. `verifyChecksum` checks file integrity. `getTableProperties` converts C++ `TableProperties` to Java. `disposeInternalJni` deletes the reader.

Control flow: Java creates a reader handle, opens a path, asks for iterators or metadata, and disposes. String paths are copied with `GetStringUTFChars` and released before exception propagation.

State and persistence behavior: The reader owns native open-file/metadata state for an existing SST file. It does not mutate RocksDB state.

Dependencies and integration points: Depends on generated `org_rocksdb_SstFileReader.h`, `rocksdb/sst_file_reader.h`, options/env/comparator headers, and `portal.h`. Iterators returned here are managed by `sst_file_reader_iterator.cc`.

Risks: `getTableProperties` dereferences `tp.get()` without checking for null; if called before open or after an error path that yields no properties, it may crash. Iterator ownership is transferred to Java and must be disposed.

Test signals: Tests should open valid and invalid SST paths, iterate contents, verify checksums, assert table properties after open, and ensure pre-open property calls are handled by Java or fail predictably.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/sst_file_readerjni.cc -->
