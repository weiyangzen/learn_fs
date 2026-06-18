# sources/storage-engines/rocksdb/env/io_posix.cc

## Purpose
Implements concrete POSIX file and directory classes used by `fs_posix.cc`: sequential reads, random reads, mmap reads/writes, writable files, random read/write files, memory-mapped buffers, directory fsync, direct-I/O helpers, logical-block-size lookup, preallocation, range sync, and optional io_uring batched/async read support.

## Important APIs and Functions
- `IOErrorMsg` and `IOError` translate errno values to `IOStatus`, including retryable `NoSpace`, stale file, and path-not-found handling.
- `Fadvise`, `Madvise`, `PosixWrite`, and `PosixPositionedWrite` wrap platform behavior and large write chunking.
- `LogicalBlockSizeCache` and `PosixHelper` read `/sys/dev/block/.../queue/{logical_block_size,max_sectors_kb}` with defaults.
- `PosixSequentialFile::{Read,PositionedRead,Skip,InvalidateCache}` implements buffered and direct sequential access.
- `PosixRandomAccessFile::{Read,MultiRead,Prefetch,ReadAsync,GetFileSize,Hint,InvalidateCache}` implements pread, io_uring batching, async read, and cache hints.
- `PosixMmapReadableFile` and `PosixMmapFile` implement mmap read and mmap write.
- `PosixWritableFile` implements append, positioned append, truncate, close, sync/fsync, fallocate, range sync, write lifetime hints, cache invalidation, and unique IDs.
- `PosixRandomRWFile`, `PosixMemoryMappedFileBuffer`, and `PosixDirectory` cover random RW, raw mmap buffer cleanup, and directory sync semantics.

## Control Flow
Read paths loop on `EINTR` and stop on EOF or short direct-I/O sectors. `MultiRead` uses a thread-local io_uring when available: prepares SQEs up to queue capacity, submits with `io_uring_submit_and_wait`, reaps CQEs, resubmits short or transient requests, and falls back to serialized reads when ring initialization is unavailable. `ReadAsync` allocates a `Posix_IOHandle`, prepares one read SQE, submits it, and returns a handle/deleter for `Poll`/`AbortIO`. mmap writes allocate/map regions, append via `memcpy`, sync with `msync` plus fd sync, unmap, and truncate unused preallocated space on close. Directory fsync skips or redirects some btrfs cases, especially syncing the renamed new file for rename operations.

## State and Persistence
Persistent effects include file writes, truncation, preallocation/hole punching, mmap-backed writes, sync/fsync/fdatasync, range sync, and directory fsync. Runtime state includes file descriptors, `FILE*`, logical sector size, direct-I/O flags, mmap pointers and offsets, writable `filesize_`, fallocate/range-sync capability flags, io_uring handles, and directory filesystem type.

## Dependencies and Integration Points
Depends on Linux/macOS/AIX/POSIX syscalls (`pread`, `write`, `pwrite`, `mmap`, `msync`, `fsync`, `fdatasync`, `fallocate`, `sync_file_range`, `statfs`, `ioctl`, `fcntl`, `readahead`, `posix_fadvise`, `posix_madvise`) plus RocksDB helpers for I/O stats, coding, sync points, and slices. It is instantiated by `PosixFileSystem` in `fs_posix.cc` and implements the low-level behavior behind RocksDB `FS*File` interfaces.

## Risks and Edge Cases
- Direct I/O alignment is enforced with assertions, so release builds may rely on kernel errors if callers pass unaligned buffers/offsets.
- `PosixWrite` and `PosixPositionedWrite` do not explicitly handle a zero-byte successful write while bytes remain; such behavior would spin, though regular files should not return zero for nonzero writes.
- `MultiRead` is complex and must maintain io_uring queue accounting precisely; error teardown destroys the thread-local ring to avoid stale SQEs.
- `ReadAsync` returns `Busy` if no SQE is available and must not publish a handle in that case.
- `PosixMmapFile::Close` computes `unused = limit_ - dst_`; this assumes a region has been mapped before close, which is normally true after append but is a fragile invariant for empty mmap files.
- Directory fsync behavior is filesystem-specific; btrfs rename handling intentionally syncs the new file instead of the directory.

## Test Signals
`io_posix_test.cc` covers `LogicalBlockSizeCache` caching/refcount behavior, `PosixWritableFile::Truncate` seek positioning after shrink and extend, and btrfs rename fsync error preservation. Additional valuable tests would cover io_uring `MultiRead` partial reads/errors, `ReadAsync` SQ-full behavior, mmap empty-file close, direct-I/O alignment failures, ZFS/WSL `sync_file_range` fallback, and write zero-progress handling.
