<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/example/helloworld/main.go -->
# sources/user-network-fs/go-nfs/example/helloworld/main.go

## Purpose
Shows a minimal read-only NFS server backed by an in-memory billy filesystem.

## Important APIs, Types, and Functions
Defines `ROFS` capability wrapper and `main`.

## Control Flow
The program listens on an ephemeral TCP port, creates a memfs file `hello.txt`, wraps memfs as read-only, layers null auth and caching handlers, and calls `nfs.Serve`.

## State and Persistence Behavior
State is in-memory only and lasts for the process.

## Dependencies and Integration Points
Depends on billy memfs, go-nfs helpers, and TCP listener setup.

## Risks and Edge Cases
No authentication or export selection; ephemeral port is printed for manual use. It is an example, not hardened server code.

## Test Signals
Manual signal is mounting the printed address and reading `hello.txt`; build tests catch API drift.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/example/helloworld/main.go -->
