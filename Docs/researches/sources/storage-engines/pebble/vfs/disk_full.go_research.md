# Research: sources/storage-engines/pebble/vfs/disk_full.go

## Purpose
`vfs/disk_full.go` implements `OnDiskFull`, an FS wrapper that detects `ENOSPC`, invokes a callback once per write generation, blocks concurrent write operations while the callback runs, and retries eligible operations once.

## Important APIs, Types, And Functions
`OnDiskFull(fs, fn)` returns an `enospcFS`. `enospcFS` wraps write-oriented FS methods and file methods, tracks a generation counter, and uses a mutex/condition variable around callback execution. `waitUntilReady` waits if an ENOSPC callback is active. `handleENOSPC` elects the first failing operation in a generation to run the callback. `enospcFile` wraps `Write`, `WriteAt`, `Sync`, `SyncData`, and `SyncTo`. `isENOSPC` unwraps Cockroach errors to detect `syscall.ENOSPC`.

## Control Flow
Before a write-capable operation, the wrapper loads an even generation or waits for an odd generation to finish. If the operation returns ENOSPC, the first goroutine for that generation increments to odd, runs the callback outside the mutex, increments to the next even generation, and broadcasts. Other goroutines from the same generation wait only for that callback. Most operations retry once; sync operations trigger the callback but do not retry.

## State And Persistence
The wrapper does not persist its own state. It affects persistence by giving callers a chance to free disk space, for example by deleting a ballast file, before retrying writes. Underlying files and directories persist through the wrapped FS.

## Dependencies And Integration Points
It depends on the `vfs.FS` and `vfs.File` interfaces, Cockroach error unwrapping, syscall errno, and condition variables. Pebble can wrap its FS to coordinate disk-full remediation across WAL, manifest, flush, and compaction writes.

## Risks And Edge Cases
Retried writes use remaining bytes after partial writes, so underlying write semantics must be respected. Sync cannot safely be retried because a later successful fsync does not prove earlier writes survived. If the callback fails to free space, the retry returns ENOSPC and later generations may invoke callbacks again. Read-only operations are not blocked.

## Test Signals
Tests cover all wrapped FS write operations, file `Write` partial retry, non-retry `Sync`, one callback for concurrent same-generation ENOSPCs, error unwrapping, invocation counts, and benchmark overhead when no ENOSPC occurs.
