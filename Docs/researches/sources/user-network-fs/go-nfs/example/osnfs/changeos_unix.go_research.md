<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/example/osnfs/changeos_unix.go -->
# sources/user-network-fs/go-nfs/example/osnfs/changeos_unix.go

## Purpose
Adds Unix special-file and hard-link operations to the writable OS-backed NFS example.

## Important APIs, Types, and Functions
`COS.Mknod`, `Mkfifo`, `Link`, and `Socket` implement the `nfs.UnixChange` interface on Unix builds.

## Control Flow
Methods map NFS major/minor into a device number, call Unix mknod/mkfifo/link, or create and bind a Unix socket.

## State and Persistence Behavior
State is the special filesystem object created in the exported OS tree; socket fd is not explicitly closed after bind.

## Dependencies and Integration Points
Used by `nfs_onmknod.go` and `nfs_onlink.go` when the example handler is mounted.

## Risks and Edge Cases
Requires privileges for device nodes, does not close socket fd, and `Link` expects its source path interpretation to match handler call sites.

## Test Signals
Manual client tests for `mknod`, FIFO creation, socket creation, and hard links exercise this file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/example/osnfs/changeos_unix.go -->
