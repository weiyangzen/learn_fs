<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/fadvise_generic.go -->
# sources/storage-engines/pebble/vfs/fadvise_generic.go

## Purpose
Provides no-op advisory read hint functions on non-Linux platforms.

## Important APIs, Types, and Functions
`fadviseRandom` and `fadviseSequential` accept a file descriptor and return nil.

## Control Flow
Both functions immediately return nil. `vfs.RandomReadsOption` and `vfs.SequentialReadsOption` can call them without platform checks.

## State and Persistence Behavior
No state or persistence; no OS calls are made.

## Dependencies and Integration Points
Used by `vfs.go` open options on platforms where `unix.Fadvise` is unavailable or not used. Built under `!linux`.

## Risks and Edge Cases
Read-hint options silently do nothing, so performance behavior differs from Linux. Callers must treat these hints as best-effort.

## Test Signals
No direct tests. `vfs_test.go` and broader VFS tests exercise open options structurally, while Linux-specific behavior is implemented in `fadvise_linux.go`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/fadvise_generic.go -->
