# sources/user-network-fs/rclone/fs/sync/rc.go

## Purpose
This file registers RC endpoints for sync, copy, and move directory operations.

## Important APIs, Types, and Functions
- Init registers `sync/sync`, `sync/copy`, and `sync/move`.
- `rcSyncCopyMove(ctx, in, name)` resolves source/destination filesystems and dispatches to `Sync`, `CopyDir`, or `MoveDir`.

## Control Flow
For each operation name, an RC call is added with help text. At call time, `srcFs` and `dstFs` are required through `rc.GetFsNamed`. Optional `createEmptySrcDirs` is parsed if present. For move, optional `deleteEmptySrcDirs` is also parsed. Missing optional bools default false; invalid bools return parameter errors.

## State and Persistence
The file registers global RC calls at package initialization. The operation handlers can mutate source and destination remotes by copying, deleting, moving, and creating directories according to the chosen operation.

## Dependencies and Integration Points
It depends on `fs/rc` and the sync engine in `sync.go`. It integrates RC clients with rclone's core sync/copy/move behavior and filesystem cache/config resolution.

## Risks and Edge Cases
These endpoints are destructive for `sync` and `move`; server auth policy must protect them unless explicitly disabled. The closure over `name` relies on Go's per-iteration range variable semantics in the targeted Go version. Missing optional booleans are accepted, but malformed values fail.

## Test Signals
`sync/rc_test.go` exercises all three registered endpoints against local test remotes and verifies resulting source/destination contents.
