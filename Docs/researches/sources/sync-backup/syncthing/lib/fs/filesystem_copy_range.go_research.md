# sources/sync-backup/syncthing/lib/fs/filesystem_copy_range.go

## Purpose
Maintains the registry and dispatch function for file range copy implementations.

## Important APIs, Types, and Functions
`copyRangeMethods` map, mutex `mut`, `copyRangeImplementation`, `registerCopyRangeImplementation`, and public `CopyRange`.

## Control Flow
Platform files register implementations in `init`. `CopyRange` looks up the requested `CopyRangeMethod` and calls it with source/destination files, offsets, and size; missing methods return `syscall.ENOTSUP`.

## State and Persistence Behavior
Process-local registry only. Copy implementations mutate destination file contents and size; this dispatcher does not.

## Dependencies and Integration Points
Called by higher-level file synchronization code needing efficient range copies. Integrates with basic-file unwrapping and platform copy syscalls in sibling files.

## Risks
Registration is global and method collisions overwrite previous implementations. Missing method support is runtime, not compile-time. Callers must choose fallback behavior.

## Test Signals
`filesystem_copy_range_test.go` iterates the registry and validates data, size, offsets, and expected errors for each registered implementation.
