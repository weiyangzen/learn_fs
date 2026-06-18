<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/fadvise_linux.go -->
# sources/storage-engines/pebble/vfs/fadvise_linux.go

## Purpose
Implements Linux advisory read hints used by VFS open options.

## Important APIs, Types, and Functions
`fadviseRandom` calls `unix.Fadvise` with `FADV_RANDOM`; `fadviseSequential` calls it with `FADV_SEQUENTIAL`.

## Control Flow
When `RandomReadsOption` or `SequentialReadsOption` is applied to a file with a valid descriptor, the corresponding helper sends a whole-file advisory hint to the kernel. The caller ignores the returned error.

## State and Persistence Behavior
No Pebble state or durable data is changed. The kernel may adjust readahead behavior for the descriptor.

## Dependencies and Integration Points
Depends on `golang.org/x/sys/unix` and is called from `vfs.go` open options. It is Linux-only.

## Risks and Edge Cases
Errors are intentionally ignored by open-option callers, so unsupported filesystems/descriptors silently proceed without the hint. The hint uses offset and length zero to mean the whole file.

## Test Signals
No direct test in this shard. `fd_test.go` verifies wrappers preserve file descriptors so open options can reach descriptor-backed implementations.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/fadvise_linux.go -->
