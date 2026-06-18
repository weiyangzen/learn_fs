<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onfsinfo.go -->
# sources/user-network-fs/go-nfs/nfs_onfsinfo.go

## Purpose
Implements NFS FSINFO with advertised transfer sizes and capability flags.

## Important APIs, Types, and Functions
`onFSInfo` and `FSInfoProperty*` constants are central.

## Control Flow
It reads a handle, resolves it, writes post-op attrs, fills an inline `fsinfores` with large read/write limits, dtpref, max filesize, nanosecond delta, and properties inferred from filesystem interfaces/capabilities.

## State and Persistence Behavior
No persistent state.

## Dependencies and Integration Points
Depends on billy symlink/write capability, `tryStat`, and XDR encoding.

## Risks and Edge Cases
Advertised limits are guesses and not user-configurable; hard-link support is inferred from symlink support, which is imprecise.

## Test Signals
FSINFO tests should assert property bits for read-only, writable, and symlink-capable filesystems.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onfsinfo.go -->
