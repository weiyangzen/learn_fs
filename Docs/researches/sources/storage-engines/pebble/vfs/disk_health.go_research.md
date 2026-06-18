# Research: sources/storage-engines/pebble/vfs/disk_health.go

## Purpose
`vfs/disk_health.go` implements disk write statistics and slow-disk detection for Pebble's VFS. It wraps files and write-oriented filesystem metadata operations, reports operations that exceed a threshold, and aggregates bytes written by disk write category.

## Important APIs, Types, And Functions
`OpType` enumerates monitored operations and has string/redaction formatting. `DiskWriteCategory`, `WriteCategoryUnspecified`, `DiskWriteStatsAggregate`, and `DiskWriteStatsCollector` provide write-byte aggregation. `diskHealthCheckingFile` wraps a `File`, tracks one in-flight file operation in a packed atomic, runs a ticker, times `Write`, `WriteAt`, `Preallocate`, `Sync`, `SyncData`, and `SyncTo`, and increments category bytes.

`DiskSlowInfo` formats slow-operation reports. `diskHealthCheckingFS` wraps an FS, tracks concurrent metadata operations in reusable slots, starts/stops a ticker goroutine, and wraps `Create`, `ReuseForWrite`, `OpenReadWrite`, and directories. `WithDiskHealthChecks` returns either the inner FS or a wrapper plus closer.

## Control Flow
For file operations, `timeDiskOp` packs start delta, write size, and op type into `lastWritePacked`, runs the operation, then clears it. A ticker periodically checks whether the current operation duration exceeds the threshold and calls `onSlowDisk`. For filesystem operations, `timeFilesystemOp` claims a slot, records name/op/start time, runs the operation, then clears the slot; a separate ticker scans all in-flight slots and reports slow metadata operations.

## State And Persistence
The wrapper's state is transient: ticker goroutines, stop channels, packed atomics, slot slices, create times, and byte counters. It does not persist data itself; it delegates to the underlying FS. `DiskWriteStatsCollector` accumulates in-memory per-category totals.

## Dependencies And Integration Points
It depends on `crtime` monotonic clocks, redact formatting, sync/atomic primitives, `vfs.FS` and `vfs.File`, and Pebble options that install disk-health checks. It integrates with event listeners through the `onSlowDisk` callback and with metrics through the stats collector.

## Risks And Edge Cases
`diskHealthCheckingFile` assumes no concurrent write-like operations on the same file handle and panics if detected. The packed timestamp supports about 34 years of uptime; larger deltas panic. Write sizes are rounded down to KiB and capped under about 1 GiB. `OpenReadWrite` wraps only stats collection with threshold zero, so slow detection is disabled there. Ticker close/reuse must avoid leaking goroutines.

## Test Signals
Tests cover byte aggregation, slow file writes and syncs, op-type packing limits, packing/unpacking edge cases, delta overflow panic, slow metadata operations, repeated close/reuse of FS wrapper, and `DiskSlowInfo` text containing full path, op, size, and duration.
