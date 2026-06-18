<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/sst_file_manager.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/sst_file_manager.cc

Purpose: Bridges Java `SstFileManager` to C++ `ROCKSDB_NAMESPACE::SstFileManager` for tracking and throttling SST/trash file deletion and space usage.

Important APIs/types/functions: `newSstFileManager` calls `NewSstFileManager` with an `Env`, optional `Logger`, delete rate, trash ratio, and delete chunk size. Accessors/mutators expose max allowed space, compaction buffer size, max-space flags, total size, tracked files map, delete rate, and max trash DB ratio. Disposal deletes the heap `std::shared_ptr<SstFileManager>` wrapper.

Control flow: Constructor receives native `Env` and optional shared logger handles, calls the factory, checks `Status`, and wraps the raw manager in a shared pointer. Map conversion for tracked files builds a Java `HashMap<String,Long>`.

State and persistence behavior: The manager tracks RocksDB-managed SST/trash files and can affect deletion throttling and allowed-space decisions. The file itself stores process-local shared pointer state.

Dependencies and integration points: Depends on `rocksdb/sst_file_manager.h`, generated `org_rocksdb_SstFileManager.h`, conversion utilities, and `portal.h`. The returned shared pointer is typically installed into DB options.

Risks: If `NewSstFileManager` returns an error, the code deletes any non-null raw manager and throws, but still proceeds to allocate and return a shared pointer after throwing; JNI callers will usually observe the pending exception, but the native return path is not guarded by an explicit `return 0`. Map conversion can leak local references on large maps if helper behavior does not clean each pair. Handle misuse remains unsafe.

Test signals: Tests should construct with and without a logger, assert failed construction raises, verify tracked file map conversion, mutate rate/ratio/space settings, and validate disposal under leak checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/sst_file_manager.cc -->
