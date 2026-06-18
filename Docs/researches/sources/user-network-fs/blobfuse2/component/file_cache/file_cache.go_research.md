# sources/user-network-fs/blobfuse2/component/file_cache/file_cache.go

## Purpose

`file_cache.go` implements Blobfuse2's local file cache component. It downloads remote files into a local temp path, serves reads and writes through local file descriptors, flushes dirty handles back to storage, merges local and remote directory/attribute views, and coordinates eviction policy state.

## Important APIs, Types, and Functions

`FileCache` stores temp path, file locks, cache policy, config flags (`createEmptyFile`, `allowNonEmpty`, `offloadIO`, `syncToFlush`, `syncToDelete`, `lazyWrite`, `hardLimit`), size/time settings, missed chmod tracking, and async close wait group. `FileCacheOptions` defines all config keys. Major methods include `Start`, `Stop`, `GenConfig`, `Configure`, `OnConfigChange`, `StatFs`, `GetPolicyConfig`, `ReadDir`, `StreamDir`, `IsDirEmpty`, `CreateFile`, `OpenFile`, `ReleaseFile`, `ReadFile`, `ReadInBuffer`, `WriteFile`, `SyncFile`, `FlushFile`, `GetAttr`, `RenameFile`, `TruncateFile`, `Chmod`, `Chown`, `DeleteFile`, `DeleteDir`, `RenameDir`, and `FileUsed`.

## Control Flow

Configuration expands and validates the temp path, rejects mount-path conflicts and disallowed non-empty temp directories, derives max cache size from filesystem free space unless configured, sets default permissions from `allow-other`, builds an LRU policy config, and records hard-limit watermarks. Opens check policy membership and local file freshness through `isDownloadRequired`; if a download is required, they optionally delete stale local files, create directories, enforce hard-limit capacity, copy from the next component, set local mode and timestamps, update stats, then open the local file and return a handle. Writes use `syscall.Pwrite`, mark handles dirty, and periodically refresh policy validity. Reads use `syscall.Pread` or full-file reads from the local descriptor. Flush serializes dirty uploads with a per-file lock, duplicates and closes the fd to flush kernel buffers, opens a read handle, calls `CopyFromFile`, clears dirty state, and applies missed chmods. Release flushes, closes the file, decrements lock counts, and invalidates or purges local cache depending on fsync state.

## State and Persistence Behavior

The component persists cached file bytes and directories under `tmpPath`. It tracks cache policy state in the selected policy, per-path open/download locks in `common.LockMap`, missed chmods in `sync.Map`, dirty/fsynced/cached bits on handles, and file-cache metrics through `stats_manager`. Storage state changes are delegated to the next pipeline component through create/delete/rename/truncate/chmod/chown/copy calls.

## Dependencies and Integration Points

It integrates deeply with Blobfuse pipeline interfaces in `internal.Component`, handle state in `handlemap`, common helpers for locks, temp cleanup, usage, and permissions, config change listeners, stats collection, and the LRU policy implementation. The next component supplies storage operations and transfer primitives `CopyToFile` and `CopyFromFile`.

## Risks and Edge Cases

High-risk areas are local/remote divergence when `createEmptyFile` is false, recoverability of storage 404s, path safety under `tmpPath`, permission changes needed for uploads, concurrent flush/release/sync operations, hard-limit accounting based on directory usage, cache invalidation timing, and stale local entries after rename/delete failures. `isLocalDirEmpty` ignores `os.Open` errors before deferring close, which can panic if called on an invalid path. Some async invalidation calls can race with later opens if not protected by file locks.

## Test Signals

`file_cache_test.go` is broad: config defaults and errors, directory merging, create/open/read/write/flush/release, sync modes, rename/delete/truncate/chmod/chown, symlink cache paths, lazy write, StatFS, refresh, hard limits, empty-directory cleanup, concurrent flush serialization, and download-failure cleanup.
