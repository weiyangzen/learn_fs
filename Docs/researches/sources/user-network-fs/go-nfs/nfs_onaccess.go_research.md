<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onaccess.go -->
# sources/user-network-fs/go-nfs/nfs_onaccess.go

## Purpose
Implements NFS ACCESS, returning allowed access bits and post-op attributes.

## Important APIs, Types, and Functions
`onAccess` is the handler.

## Control Flow
It reads a file handle and requested mask, resolves the handle, reads the mask, writes OK status and post-op attrs, and strips write-related bits when the filesystem lacks write capability.

## State and Persistence Behavior
No persistent state; observes filesystem capabilities and attributes.

## Dependencies and Integration Points
Depends on `Handler.FromHandle`, billy capability checks, `tryStat`, and XDR.

## Risks and Edge Cases
Permission checks are coarse and do not inspect actual mode bits, uid/gid, or path-specific ACLs.

## Test Signals
ACCESS tests should compare masks on read-only and writable handlers and validate stale/invalid handle errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onaccess.go -->
