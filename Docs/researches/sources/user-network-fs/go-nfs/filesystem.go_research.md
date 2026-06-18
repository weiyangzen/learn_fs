<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/filesystem.go -->
# sources/user-network-fs/go-nfs/filesystem.go

## Purpose
Defines the filesystem-level statistics structure used by the NFS FSSTAT procedure.

## Important APIs, Types, and Functions
`FSStat` contains total/free/available sizes and files plus `CacheHint`.

## Control Flow
`onFSStat` fills defaults and lets the user handler override the struct.

## State and Persistence Behavior
No behavior or persistence in this file.

## Dependencies and Integration Points
Part of the `Handler.FSStat` integration point.

## Risks and Edge Cases
Fields must match XDR ordering expected by NFSv3 clients.

## Test Signals
FSSTAT procedure tests should assert encoded values after handler customization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/filesystem.go -->
