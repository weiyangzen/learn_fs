# Research: sources/storage-engines/pebble/vfs/disk_full_test.go

## Purpose
`vfs/disk_full_test.go` validates the `OnDiskFull` wrapper's ENOSPC callback, retry, and concurrency semantics.

## Important APIs, Types, And Functions
`filesystemWriteOps` enumerates FS operations expected to handle ENOSPC: `Create`, `Lock`, `ReuseForWrite`, `Link`, `MkdirAll`, `Remove`, `RemoveAll`, and `Rename`. `TestOnDiskFull_FS` checks callback and retry per operation. `TestOnDiskFull_File` checks file `Write` and `Sync`. `TestOnDiskFull_Concurrent` checks one callback for a concurrent generation. `enospcMockFS` and `enospcMockFile` inject wrapped ENOSPC errors and count invocations. `BenchmarkOnDiskFull` measures no-error write overhead.

## Control Flow
Tests configure the mock FS to return ENOSPC a controlled number of times. FS method tests expect the wrapper to invoke the callback and retry successfully. File write tests simulate a partial write before ENOSPC and expect the retry to write the remainder. Sync tests expect the callback but a returned error. The concurrent test synchronizes failing goroutines so they all belong to one generation.

## State And Persistence
State is entirely in-memory: ENOSPC counters, invocation counters, callback counters, and condition-variable synchronization. No real filesystem data is required.

## Dependencies And Integration Points
The tests use `require`, Cockroach error wrapping, syscall ENOSPC, Go sync primitives, and the `vfs` interfaces. They directly exercise the wrapper contract that Pebble write paths rely on during full-disk events.

## Risks And Edge Cases
The mock must wrap `syscall.ENOSPC` to verify deep unwrapping. Concurrent test reliability depends on all goroutines consuming ENOSPC before retry proceeds. The suite does not test `SyncData`, `SyncTo`, `WriteAt`, or callback panics, so those remain residual risk.

## Test Signals
Signals include exactly one callback for one failing generation, exactly two underlying invocations for retried FS operations, correct partial-write byte accounting, no sync retry, and low wrapper overhead in the benchmark.
