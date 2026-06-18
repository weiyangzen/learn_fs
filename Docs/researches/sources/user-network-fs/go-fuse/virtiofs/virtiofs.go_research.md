<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/virtiofs/virtiofs.go -->
# sources/user-network-fs/go-fuse/virtiofs/virtiofs.go

## Purpose
Connects a go-fuse raw filesystem to a vhost-user virtio-fs socket.

## Important APIs, Types, and Functions
`ServeFS(sockpath, rawFS, opts)` is the exported entry point.

## Control Flow
It listens on a Unix socket, disables splice in mount options, creates a `fuse.ProtocolServer`, accepts connections, constructs a `vhostuser.Device` whose handler calls `HandleRequest`, then serves vhost-user control messages until disconnect.

## State and Persistence Behavior
State is per-accepted connection device/server state plus the shared protocol server. The listener remains active until accept fails.

## Dependencies and Integration Points
Depends on `net.UnixConn`, `fuse.ProtocolServer`, and `internal/vhostuser`. Used by QEMU tests.

## Risks and Edge Cases
The function logs fatally on listen errors and has no shutdown context. It serially handles accepted connections and enables verbose vhost-user debug logging.

## Test Signals
End-to-end QEMU tests are the main validation; tests should also cover socket bind failure and reconnect behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/virtiofs/virtiofs.go -->
