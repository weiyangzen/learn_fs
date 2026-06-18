<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onfsstat.go -->
# sources/user-network-fs/go-nfs/nfs_onfsstat.go

## Purpose
Implements NFS FSSTAT with defaults that handlers can override.

## Important APIs, Types, and Functions
`onFSStat` is the handler.

## Control Flow
It reads a handle, resolves it, initializes huge default capacity values, zeros available space for read-only filesystems, calls `Handler.FSStat`, and writes post-op attrs plus the final stats.

## State and Persistence Behavior
No persistent state; handler may compute live filesystem statistics.

## Dependencies and Integration Points
Depends on `FSStat`, billy capabilities, handler override, and XDR.

## Risks and Edge Cases
Defaults are unrealistic and may mislead clients if handlers do not override. Handler errors are mapped coarsely unless already `NFSStatusError`.

## Test Signals
FSSTAT tests should verify defaults, read-only adjustment, and custom handler overrides.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onfsstat.go -->
