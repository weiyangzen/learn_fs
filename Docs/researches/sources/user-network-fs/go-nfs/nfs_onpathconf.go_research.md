<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onpathconf.go -->
# sources/user-network-fs/go-nfs/nfs_onpathconf.go

## Purpose
Implements NFS PATHCONF with static path configuration limits.

## Important APIs, Types, and Functions
`PathNameMax` and `onPathConf` are central.

## Control Flow
It reads a handle, resolves it, writes post-op attrs, and encodes static link/name/truncation/chown/case flags.

## State and Persistence Behavior
No persistent state.

## Dependencies and Integration Points
Used by clients after FSINFO; depends on `tryStat` and XDR.

## Risks and Edge Cases
Static `LinkMax=1` conflicts with hard-link support in some handlers; case sensitivity and chown restriction are not derived from the backing filesystem.

## Test Signals
PATHCONF tests should assert constants and stale handle behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onpathconf.go -->
