# sources/storage-engines/rocksdb/env/io_posix.h

## Purpose
Declares POSIX-backed implementations of RocksDB file interfaces and helper utilities used by the POSIX filesystem. It also declares optional io_uring request state, TSAN mmap annotations, direct-I/O alignment helpers, logical block-size caching, and platform fallback constants for fadvise/madvise.

## Important APIs and Types
- `IOErrorMsg` and `IOError` are shared status builders.
- `TsanMappedMemoryInfo` and `TsanAnnotateMappedMemory` reset TSAN shadow state for new mmap/io_uring mappings and expose sync-point payloads.
- `PosixHelper` provides unique file IDs and logical-block/max-sector lookup.
- `LogicalBlockSizeCache` caches per-directory logical block sizes with refcounts on Linux.
- `Posix_IOHandle`, `UpdateResult`, and `FinalizeAsyncRead` support io_uring async completion.
- Concrete classes: `PosixSequentialFile`, `PosixRandomAccessFile`, `PosixWritableFile`, `PosixMmapReadableFile`, `PosixMmapFile`, `PosixRandomRWFile`, `PosixMemoryMappedFileBuffer`, and `PosixDirectory`.

## Control Flow
The header defines interface contracts and state fields. Direct-I/O helpers test power-of-two sector alignment. io_uring helpers translate CQE results into `FSReadRequest` status/result and invoke callbacks. Concrete classes expose RocksDB virtual methods that are implemented in `io_posix.cc`; constructors capture descriptors, filenames, options, and alignment values.

## State and Persistence
Declared runtime state includes file descriptors, `FILE*`, direct-I/O flags, logical sector sizes, mmap region pointers, file offsets, preallocation flags, range-sync support, thread-local io_uring pointers, writable file sizes, and directory btrfs detection. Persistent effects are performed by the implementations.

## Dependencies and Integration Points
Includes optional `liburing`, pthread, sys/uio, `rocksdb/env.h`, `rocksdb/file_system.h`, `rocksdb/io_status.h`, sync points, mutex/thread-local utilities, and platform headers. These classes are consumed by `fs_posix.cc` and surfaced through RocksDB's `FS*File` abstractions.

## Risks and Edge Cases
- Compatibility macros define newer io_uring setup flags when older headers lack them; runtime kernels can still reject the flags.
- `UpdateResult` has nuanced behavior for zero-byte CQEs, partial direct-I/O sectors, async versus synchronous callers, and fallback read-again signaling.
- `LogicalBlockSizeCache::Size()` does not lock in the header declaration, while other accessors do; implementation/use should consider concurrent reads.
- The file includes test utilities in production declarations for sync-point instrumentation.

## Test Signals
`io_posix_test.cc` directly covers `LogicalBlockSizeCache` and indirectly exercises `PosixWritableFile`/`PosixDirectory` through the default filesystem. Sync-point hooks also support deterministic tests for TSAN annotation and io_uring branches elsewhere.
