<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onrmdir.go -->
# sources/user-network-fs/go-nfs/nfs_onrmdir.go

## Purpose
Implements NFS RMDIR by delegating to REMOVE.

## Important APIs, Types, and Functions
`onRmDir` simply calls `onRemove`.

## Control Flow
All parsing, validation, deletion, and response behavior are inherited from `onRemove`.

## State and Persistence Behavior
Persistent state is directory deletion through the backing filesystem.

## Dependencies and Integration Points
Depends entirely on `nfs_onremove.go`.

## Risks and Edge Cases
RMDIR-specific status distinctions are not represented here; non-directory removal through RMDIR may map according to billy `Remove` rather than NFS expectations.

## Test Signals
RMDIR tests should include non-directory target, non-empty directory, and successful empty directory removal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onrmdir.go -->
