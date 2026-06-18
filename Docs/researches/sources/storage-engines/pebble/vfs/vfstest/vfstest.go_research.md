<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/vfstest/vfstest.go -->
# sources/storage-engines/pebble/vfs/vfstest/vfstest.go

## Purpose
Defines small test helpers for VFS consumers.

## Important APIs, Types, and Functions
`DiscardFile` is a `vfs.File` implementation backed by `discardFile`. It accepts writes, returns requested byte counts for reads, and no-ops sync, preallocation, close, and prefetch.

## Control Flow
Every method on `discardFile` returns immediately with success-like values. `Read` and `ReadAt` report `len(p)` without filling the buffer. `Fd` returns 0 rather than `vfs.InvalidFd`.

## State and Persistence Behavior
No state is stored and no bytes are persisted. It is a sink/source stub for tests and benchmarks.

## Dependencies and Integration Points
Lives in `vfstest` for tests that need a cheap file-like object satisfying the full `vfs.File` interface.

## Risks and Edge Cases
`Fd` returning 0 can look like a real descriptor on Unix stdin, so callers that use `Fd` should not use `DiscardFile` unless that behavior is acceptable. `Stat` returns nil info and nil error, which may surprise callers expecting metadata.

## Test Signals
No direct test in this file. Compile-time interface satisfaction comes from assigning `DiscardFile` as `vfs.File`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/vfstest/vfstest.go -->
