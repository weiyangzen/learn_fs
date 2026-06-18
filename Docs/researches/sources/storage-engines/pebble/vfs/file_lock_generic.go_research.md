<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/file_lock_generic.go -->
# sources/storage-engines/pebble/vfs/file_lock_generic.go

## Purpose
Provides the fallback `Lock` implementation for platforms without explicit Unix or Windows file locking support.

## Important APIs, Types, and Functions
The fallback `Lock` method returns an error saying file locking is not implemented on the current `GOOS/GOARCH`.

## Control Flow
A call to `Lock` immediately returns nil closer and a formatted error with safe runtime values.

## State and Persistence Behavior
No file is created or modified because locking is unsupported in this fallback.

## Dependencies and Integration Points
Completes the `defaultFS` implementation of `vfs.FS` for unsupported platforms. Built when none of the Unix or Windows lock build tags apply.

## Risks and Edge Cases
The code spells the receiver as `defFS`, while the main type is `defaultFS`; if this build tag is selected, that mismatch would fail compilation unless another type alias exists outside this shard. Supported Pebble platforms likely use the Unix or Windows implementations.

## Test Signals
`file_lock_test.go` exercises lock behavior on supported platforms. There is no fallback-platform test here.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/file_lock_generic.go -->
