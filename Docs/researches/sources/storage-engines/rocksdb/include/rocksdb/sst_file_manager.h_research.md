# sources/storage-engines/rocksdb/include/rocksdb/sst_file_manager.h

Purpose: This header defines the public `SstFileManager` interface and factories. The manager tracks SST and blob file sizes, enforces optional space caps, and rate-limits deletion of SST/blob/WAL files through the delete scheduler used by DB instances.

Important APIs and types: `SstFileManager` is a thread-safe public interface whose concrete derived classes are RocksDB-internal. It exposes `SetMaxAllowedSpaceUsage()`, `SetCompactionBufferSize()`, `IsMaxAllowedSpaceReached()`, `IsMaxAllowedSpaceReachedIncludingCompactions()`, `GetTotalSize()`, `GetTrackedFiles()`, `GetDeleteRateBytesPerSecond()`, `SetDeleteRateBytesPerSecond()`, `GetMaxTrashDBRatio()`, `SetMaxTrashDBRatio()`, `GetTotalTrashSize()`, and `SetStatisticsPtr()`. `NewSstFileManager()` has a modern overload taking `Env*` plus `std::shared_ptr<FileSystem>` and a legacy `Env*` overload.

Control flow: DB instances register and unregister tracked SST/blob files through the implementation. Callers can update the max allowed space; when tracked bytes exceed it, RocksDB writes fail through background error behavior. Delete scheduling throttles file deletion based on configured bytes per second and can chunk large file truncation. Trash ratio controls whether new files bypass trash and delete immediately.

State and persistence behavior: Runtime state includes tracked filenames/sizes, total tracked size, trash size, delete-rate settings, max-space settings, compaction buffer size, and optional statistics pointer. It does not track WAL file sizes for space accounting, but its delete scheduler affects WAL deletion rate. It can be shared by multiple DBs, coordinating space and deletion behavior across them.

Dependencies and integration points: It depends on `file_system.h`, `statistics.h`, `status.h`, `Env`, and `Logger`. `DBOptions::sst_file_manager` uses it; compaction, flush, obsolete-file cleanup, delete scheduling, and DB write admission integrate with it.

Risks and edge cases: The manager only tracks SST/blob files in the first DB path according to `DBOptions` comments, which can surprise multi-path users. Setting max allowed space too low can stop writes. Deletion throttling can build trash backlog; high trash ratio triggers immediate deletion. Chunked deletion can leave partial trash files that should not be manually recovered without checking. Deprecated trash-dir arguments mostly have no effect but still influence cleanup of provided directories.

Test signals: Tests should verify tracked-file maps and total size, max-space admission failures, inclusion of ongoing compaction estimates, deletion-rate throttling and runtime changes, trash-size accounting, shared manager behavior across DBs, statistics updates, and both factory overloads.
