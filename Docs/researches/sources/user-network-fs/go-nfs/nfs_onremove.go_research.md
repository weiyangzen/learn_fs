<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onremove.go -->
# sources/user-network-fs/go-nfs/nfs_onremove.go

## Purpose
Implements NFS REMOVE and is reused for RMDIR.

## Important APIs, Types, and Functions
`onRemove` is the handler.

## Control Flow
It decodes parent/name, resolves parent, checks write capability/name length/parent directory, captures pre-op dir attrs, removes the child, invalidates the child's cached handle, and writes directory WCC.

## State and Persistence Behavior
Persistent state is deletion from the backing filesystem and handle invalidation.

## Dependencies and Integration Points
Depends on billy `Remove`, handler cache invalidation, WCC helpers, and XDR.

## Risks and Edge Cases
Same implementation for files and directories may not distinguish non-empty directory or wrong procedure status precisely; it creates a handle for deletion solely to invalidate it.

## Test Signals
REMOVE/RMDIR tests should cover file removal, empty/non-empty directories, read-only FS, stale handles, and cache invalidation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onremove.go -->
