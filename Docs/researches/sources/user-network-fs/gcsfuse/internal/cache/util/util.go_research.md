<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/util/util.go -->
# Research: sources/user-network-fs/gcsfuse/internal/cache/util/util.go

Purpose: provides low-level helpers and error sentinels for file-cache paths, cache directory creation, CRC computation, safe file deletion, memory-aligned buffers, and aligned copy behavior needed by direct-I/O cache writes.

Important APIs/types/functions: cache read error sentinels; constants `MiB`, `KiB`, `DefaultFilePerm`, `DefaultDirPerm`, `FileCache`, `SharedChunkCache`, `BufferSizeForCRC`; `CreateFile`; `GetObjectPath`; `GetDownloadPath`; `IsCacheHandleInvalid`; `CreateCacheDirectoryIfNotPresentAt`; `calculateCRC32`; `CalculateFileCRC32`; `TruncateAndRemoveFile`; `GetMemoryAlignedBuffer`; and `CopyUsingMemoryAlignedBuffer`.

Control flow: `CreateFile` creates parent directories, stats the target, adds `O_CREATE` only for missing files, and opens with requested flags and permissions. `CreateCacheDirectoryIfNotPresentAt` creates the cache directory if needed and verifies writability using `fsutil.AnonymousFile`. CRC calculation reads in 64 KiB chunks and checks context cancellation on each loop. `TruncateAndRemoveFile` truncates before removal so open file descriptors do not retain disk usage. `GetMemoryAlignedBuffer` overallocates and slices to an aligned address, retrying up to three times. `CopyUsingMemoryAlignedBuffer` validates buffer size, rounds each write size up to the configured minimum alignment, reads with `io.ReadFull`, writes padded buffers, and respects context cancellation.

State and persistence: helpers manipulate local filesystem state: cache directories, files, temp anonymous files, file contents, and deletion. There is no package-level mutable state.

Dependencies and integration points: used by file-cache creation in `internal/fs/fs.go`, downloader/cache handlers, direct-I/O sparse/chunk cache paths, and CRC validation. Depends on `cfg.CacheUtilMinimumAlignSizeForWriting`, `internal/cache/data.FileSpec`, `fsutil`, and standard filesystem APIs.

Risks: path joining uses `path` for object/cache paths and `filepath` for local parent directory creation; callers must pass platform-appropriate paths. `TruncateAndRemoveFile` returns an error for absent files. Aligned copy writes padded zero bytes and returns bytes written, not logical content bytes, which callers must interpret carefully. `unsafe` pointer alignment is platform-sensitive.

Test signals: `util_test.go` covers permissions, relative paths, sentinel error wrapping, CRC success/failure/cancellation, truncate-remove behavior with open handles, directory writability validation, alignment pointer checks, O_DIRECT offset behavior, padding, and cancellation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/util/util.go -->
