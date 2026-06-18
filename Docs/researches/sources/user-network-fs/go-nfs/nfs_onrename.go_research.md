<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onrename.go -->
# sources/user-network-fs/go-nfs/nfs_onrename.go

## Purpose
Implements NFS RENAME across paths within the same billy filesystem.

## Important APIs, Types, and Functions
`doubleWccErrorBody` and `onRename` are central.

## Control Flow
It decodes source and destination directory/name pairs, resolves both handles, rejects cross-filesystem renames, checks write capability/name lengths/parent dirs, captures pre-op WCC for both dirs, renames, invalidates the old handle, and writes both WCC blocks.

## State and Persistence Behavior
Persistent state is the backing filesystem rename and handle invalidation.

## Dependencies and Integration Points
Depends on billy `Rename`, `reflect.DeepEqual` for filesystem identity, and XDR.

## Risks and Edge Cases
Filesystem identity via `DeepEqual` can be fragile; destination handle invalidation is not explicit; overwrite semantics are delegated to billy implementation.

## Test Signals
RENAME tests should cover same dir, cross dir, overwrite, cross filesystem rejection, stale source handle, and WCC bodies.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onrename.go -->
