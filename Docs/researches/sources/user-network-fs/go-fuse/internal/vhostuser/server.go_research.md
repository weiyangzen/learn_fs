<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/vhostuser/server.go -->
# sources/user-network-fs/go-fuse/internal/vhostuser/server.go

## Purpose
Implements the vhost-user control socket protocol for configuring the backend device over a Unix domain socket.

## Important APIs, Types, and Functions
`Server`, `NewServer`, `Serve`, `Close`, `oneRequest`, feature request helpers, and the request switch over `REQ_*` define the API.

## Control Flow
`oneRequest` reads a fixed header, parses ancillary fds, optionally reads payload bytes, logs decoded messages, validates expected fd counts, dispatches to `Device` methods under `dispatchMu`, and writes replies when required.

## State and Persistence Behavior
The server owns the Unix connection and delegates persistent state to `Device`. It serializes each control request and closes no inbound fd on failed dispatch except where the device method consumes it.

## Dependencies and Integration Points
Integrates with `types.go` wire structs, `Device` setters, Unix rights parsing, and QEMU vhost-user message ordering. It is the only path from QEMU control-plane messages into queues and memory maps.

## Risks and Edge Cases
Only a subset of protocol requests is implemented; payload size uses a fixed 4 KiB buffer; all fds are made nonblocking before device code sometimes changes them; unknown operations become device errors.

## Test Signals
Virtiofs QEMU tests cover the happy path. Protocol tests should inject wrong fd counts, oversized payloads, truncated second reads, unknown requests, and `_NEED_REPLY` error responses.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/vhostuser/server.go -->
