# sources/storage-engines/rocksdb/env/io_posix_test.cc

## Purpose
Provides focused unit tests for selected POSIX I/O behaviors when `ROCKSDB_LIB_IO_POSIX` is enabled. Linux-only tests validate logical block-size cache semantics and btrfs directory fsync error handling. Cross-platform POSIX tests validate writable-file seek behavior after truncate/extend.

## Important APIs and Tests
- `LogicalBlockSizeCacheTest.Cache` verifies uncached fd fallback, directory registration, trailing slash normalization, cached lookup avoidance, and multiple cached directories.
- `LogicalBlockSizeCacheTest.Ref` verifies refcount increment/decrement and eviction at zero references.
- `PosixWritableFileTest.SeekAfterTruncate` writes, truncates smaller, appends, closes, and asserts final size.
- `PosixWritableFileTest.SeekAfterExtend` writes, truncates larger, appends, closes, and asserts final size.
- `PosixDirectoryTest.BtrfsFsyncFailedOpenDoesNotCloseInvalidFd` forces the btrfs branch via `SyncPoint` and asserts the original open error is preserved rather than overwritten by `close(-1)`.

## Control Flow
The tests use `FileSystem::Default()` and per-thread test DB paths for real filesystem interactions. Logical block-size cache tests inject lambdas instead of reading sysfs. The btrfs test creates a directory, opens `FSDirectory`, installs a sync-point callback to force `is_btrfs_`, calls `FsyncWithDirOptions` with a nonexistent renamed file, checks the error string, clears sync points, closes, and deletes the directory.

## State and Persistence
Tests create temporary files/directories under RocksDB's per-thread test path and delete them after assertions. SyncPoint global state is enabled and then cleared in the btrfs test. Logical block-size tests use local in-memory maps and counters.

## Dependencies and Integration Points
Depends on `test_util/testharness.h`, `test_util/sync_point.h`, `util/random.h`, `env/io_posix.h`, and `rocksdb/file_system.h`. It integrates with `fs_posix.cc` through `FileSystem::Default()` and with `io_posix.h` internals because the tests compile in the same namespace/configuration.

## Risks and Edge Cases
- The tests are gated by `ROCKSDB_LIB_IO_POSIX`; Linux-specific coverage is further gated by `OS_LINUX`.
- File path names for the two writable tests both include `PosixWritableFileTest_SeekAfterTruncate`, which is harmless but slightly confusing for diagnostics.
- The btrfs test checks substrings in `IOStatus::ToString()`, so wording changes can break it even if behavior remains correct.

## Test Signals
These tests provide regression signals for direct state tracked in `io_posix.cc`: truncate must reposition the fd to the logical file size before subsequent append, block-size cache must not recompute cached directories and must evict on zero refs, and btrfs rename fsync must not close an invalid descriptor or mask the open failure.
