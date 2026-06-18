<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_oncommit.go -->
# sources/user-network-fs/go-nfs/nfs_oncommit.go

## Purpose
Implements NFS COMMIT as a no-op because writes are immediately pushed to the backing store.

## Important APIs, Types, and Functions
`onCommit` handles the procedure.

## Control Flow
It reads the file handle, lets the connection drain offset/count, resolves the handle, checks write capability, writes OK, post-op attrs, and the server write verifier ID.

## State and Persistence Behavior
No data is flushed here beyond whatever backing filesystem already did; response includes `Server.ID`.

## Dependencies and Integration Points
Depends on `Handler.FromHandle`, billy write capability, `tryStat`, and connection body draining.

## Risks and Edge Cases
Returning server fault on read-only commit may not match all client expectations. It ignores offset/count entirely.

## Test Signals
Write/commit client tests should assert verifier stability and response WCC body.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_oncommit.go -->
