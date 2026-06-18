<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/syncing_file.go -->
# sources/storage-engines/pebble/vfs/syncing_file.go

## Purpose
Wraps writable files so large sequential writes periodically issue range syncs and optionally preallocate storage, reducing latency spikes from dirty page writeback while preserving full durability on close unless configured otherwise.

## Important APIs, Types, and Functions
`SyncingFileOptions` configures `NoSyncOnClose`, `BytesPerSync`, and `PreallocateSize`. `NewSyncingFile` wraps a `File`. `syncingFile.Write`, `preallocate`, `maybeSync`, `Sync`, and `Close` implement the behavior. `NewSyncingFS` wraps an FS so new files are syncing files.

## Control Flow
`Write` preallocates based on current offset, delegates to the underlying file, advances an atomic offset, then calls `maybeSync`. `maybeSync` ignores the last 1 MiB of dirty data, aligns the sync target to 4 KiB, checks `BytesPerSync`, and either calls `SyncTo` on descriptor-backed files or full `Sync` when no descriptor exists. `Sync` ratchets the sync offset to current file offset and calls `SyncData`. `Close` performs a full sync for remaining dirty data unless `NoSyncOnClose` is set, in which case it attempts `SyncTo` and closes.

## State and Persistence Behavior
`offset` and `syncOffset` are atomic so concurrent `Sync` can observe write progress, but `Write` itself is explicitly not safe for concurrent use. `preallocatedBlocks` tracks allocation progress. Range syncs may not provide durability; full `Sync`/`SyncData` on close provides the persistence guarantee unless `NoSyncOnClose` is enabled.

## Dependencies and Integration Points
Wraps `vfs.File` and is used by WAL failover writer creation. It relies on platform-specific file `SyncTo` behavior and `Fd` support. `NewSyncingFS` supports FS-level wrapping for created files; `ReuseForWrite` is intentionally unimplemented and panics.

## Risks and Edge Cases
`NoSyncOnClose` trades durability for latency and must only be used when the caller has other guarantees. If a file lacks a descriptor, periodic sync falls back to full `Sync`, which may be expensive. Preallocation errors are ignored in `Write` because the return value of `preallocate` is discarded. `syncingFS.ReuseForWrite` panics if called.

## Test Signals
`syncing_file_test.go` covers range-sync thresholds, close behavior with full versus partial syncs, `NoSyncOnClose`, and write benchmarks. `syncing_file_linux_test.go` covers Linux sync-range smoke behavior and direct-IO benchmark paths. `fd_test.go` verifies wrapper `Fd` forwarding.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/syncing_file.go -->
