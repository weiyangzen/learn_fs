<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onread.go -->
# sources/user-network-fs/go-nfs/nfs_onread.go

## Purpose
Implements NFS READ.

## Important APIs, Types, and Functions
`nfsReadArgs`, `nfsReadResponse`, `MaxRead`, and `onRead` are central.

## Control Flow
It reads handle/offset/count, opens the file, stats it, clamps count at EOF and `MaxRead`, reads with `ReadAt`, sets EOF when appropriate, and writes post-op attrs plus data.

## State and Persistence Behavior
No persistent mutation; opens and closes a backing file per request.

## Dependencies and Integration Points
Depends on billy file `ReadAt`, `Stat`, `ToFileAttribute`, and XDR.

## Risks and Edge Cases
Large offsets cast to int64 after uint64 may overflow; opening directories or special files maps to access/IO depending on billy behavior.

## Test Signals
READ tests should cover EOF, partial reads, MaxRead clamp, missing files, and large offset validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onread.go -->
