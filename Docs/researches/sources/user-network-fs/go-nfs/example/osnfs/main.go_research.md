<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/example/osnfs/main.go -->
# sources/user-network-fs/go-nfs/example/osnfs/main.go

## Purpose
Runs an NFS server exporting a real OS directory with writable metadata and Unix special-file support.

## Important APIs, Types, and Functions
`main` parses `<path> [port]`, listens, wraps `osfs.New` with `NewChangeOSFS`, layers null auth and caching handlers, and serves.

## Control Flow
The server binds to the requested or ephemeral TCP port and serves until `nfs.Serve` returns.

## State and Persistence Behavior
State is the exported OS directory and in-memory handle cache.

## Dependencies and Integration Points
Depends on billy osfs, helper handlers, and the `COS` change wrapper files.

## Risks and Edge Cases
No authentication, no export restrictions beyond the chosen path, and no graceful shutdown. Running as privileged user exposes powerful filesystem mutation operations.

## Test Signals
Manual mount/read/write/setattr tests and `go build ./example/osnfs` are the key signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/example/osnfs/main.go -->
