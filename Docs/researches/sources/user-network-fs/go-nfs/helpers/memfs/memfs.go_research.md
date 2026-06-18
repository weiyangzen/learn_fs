<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/helpers/memfs/memfs.go -->
# sources/user-network-fs/go-nfs/helpers/memfs/memfs.go

## Purpose
Implements an in-memory billy filesystem variant with stable enough file behavior for go-nfs tests.

## Important APIs, Types, and Functions
`Memory`, `New`, filesystem methods, symlink resolution, `file` methods, `fileInfo`, and flag helpers are central.

## Control Flow
Filesystem operations delegate to `storage`; opened files duplicate shared content with independent cursor/flags. Reads/writes/truncates operate on shared `content`; symlinks resolve relative targets for `Stat`, `OpenFile`, and `ReadDir`.

## State and Persistence Behavior
Persistent state is in `storage` maps and shared `content` byte slices. File handles track cursor, flags, mode, mtime, and closed state.

## Dependencies and Integration Points
Used by helper tests and examples needing a billy filesystem without OS dependencies.

## Risks and Edge Cases
Storage maps are not mutex-protected, so concurrent filesystem mutations can race. `WriteAt` semantics in storage overwrite by append/slice and may not preserve tail in all cases.

## Test Signals
Caching handler tests use this filesystem; direct tests should cover symlinks, append, truncate, rename, and concurrent access.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/helpers/memfs/memfs.go -->
