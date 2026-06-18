<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/example/osview/main.go -->
# sources/user-network-fs/go-nfs/example/osview/main.go

## Purpose
Runs a read-only view-style NFS server using `memphis` to expose an OS tree through a billy filesystem.

## Important APIs, Types, and Functions
`main` parses args, listens, builds `memphis.FromOS(...).AsBillyFS(0,0)`, wraps null auth/caching, and serves.

## Control Flow
Control flow is the same example server pattern as `osnfs`, but without writable change support.

## State and Persistence Behavior
State is the external OS tree as represented by memphis plus the in-memory handle cache.

## Dependencies and Integration Points
Depends on the external `github.com/willscott/memphis` package and go-nfs helpers.

## Risks and Edge Cases
No auth or write support; behavior depends on memphis snapshot/live-view semantics.

## Test Signals
Build and manual NFS mount tests validate the example.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/example/osview/main.go -->
