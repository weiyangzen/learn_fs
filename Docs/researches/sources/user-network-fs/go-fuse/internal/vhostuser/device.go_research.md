<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/vhostuser/device.go -->
# sources/user-network-fs/go-fuse/internal/vhostuser/device.go

## Purpose
Owns the vhost-user device state used by the virtiofs backend: request fd, virtqueues, memory regions, dirty-log table, feature negotiation, and the FUSE request callback.

## Important APIs, Types, and Functions
`Device`, `NewDevice`, `Close`, vring setters, `SetLogBase`, feature/protocol feature getters, and `VirtqElem` are the main API surface.

## Control Flow
Control-plane requests from `server.go` call setter methods under `dispatchMu`; enabling a vring starts queue processing through `Virtq.SetEnable`. The request callback returns the number of response bytes written to guest buffers.

## State and Persistence Behavior
The device owns open eventfds through its queues, mmaped memory regions, and an optional mmaped log table. `Close` tears down queues, regions, and log memory, but feature setters currently persist no negotiated mask.

## Dependencies and Integration Points
Integrates with `Server` dispatch, `Virtq` data-plane processing, `deviceRegions` address translation, Linux `mmap`/eventfd semantics, and `fuse.ProtocolServer` via `virtiofs.go`.

## Risks and Edge Cases
Queue count is hardcoded to two, feature setters ignore client masks, log-table support is partly implemented but not advertised consistently, and index bounds depend on well-formed driver messages.

## Test Signals
End-to-end coverage comes from `virtiofs` QEMU tests; focused tests should reject late `SET_VRING_KICK`, invalid queue indexes, repeated log-base setup, and close behavior with partially initialized queues.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/vhostuser/device.go -->
