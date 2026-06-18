<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_ongetattr.go -->
# sources/user-network-fs/go-nfs/nfs_ongetattr.go

## Purpose
Implements NFS GETATTR by resolving a file handle and encoding current file attributes.

## Important APIs, Types, and Functions
`onGetAttr` is the handler.

## Control Flow
It reads an opaque handle, resolves it to filesystem/path, lstat's the path, maps not-exist and I/O errors, converts stat info with `ToFileAttribute`, and writes OK plus attrs.

## State and Persistence Behavior
No mutation; observes backing filesystem metadata.

## Dependencies and Integration Points
Depends on `Handler.FromHandle`, billy `Lstat`, `ToFileAttribute`, and XDR.

## Risks and Edge Cases
Symlink handling depends on `Lstat`; missing or stale handles are distinguishable only through handler errors.

## Test Signals
GETATTR tests should cover files, dirs, symlinks, stale handles, and platform metadata.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_ongetattr.go -->
