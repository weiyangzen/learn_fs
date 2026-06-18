<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onlookup.go -->
# sources/user-network-fs/go-nfs/nfs_onlookup.go

## Purpose
Implements NFS LOOKUP including special handling for `.` and `..`.

## Important APIs, Types, and Functions
`lookupSuccessResponse` and `onLookup` are central.

## Control Flow
The handler decodes directory handle/name, verifies parent is a directory, returns the same handle for `.`, parent handle for `..`, or lstat's a child and returns a new handle plus object and directory attrs.

## State and Persistence Behavior
No mutation; may create/reuse cached handles.

## Dependencies and Integration Points
Depends on `Handler.FromHandle`, `Handler.ToHandle`, billy `Lstat`, `tryStat`, and XDR.

## Risks and Edge Cases
Root `..` returns access error rather than root; appending to path slices can alias underlying arrays if handlers reuse slices carelessly.

## Test Signals
LOOKUP tests should cover dot, dotdot, root dotdot, missing entries, and symlink lstat behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onlookup.go -->
