<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onreadlink.go -->
# sources/user-network-fs/go-nfs/nfs_onreadlink.go

## Purpose
Implements NFS READLINK.

## Important APIs, Types, and Functions
`onReadLink` is the handler.

## Control Flow
It reads a handle, resolves it, calls `fs.Readlink`, maps missing/non-symlink/access errors, writes post-op attrs and the link target string.

## State and Persistence Behavior
No mutation.

## Dependencies and Integration Points
Depends on billy symlink support, `tryStat`, and XDR.

## Risks and Edge Cases
The non-symlink check calls `fs.Stat`, which follows symlinks, so error classification can be imperfect.

## Test Signals
READLINK tests should cover valid symlink, regular file, missing file, and stale handle.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onreadlink.go -->
