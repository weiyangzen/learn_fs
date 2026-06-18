<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/vhostuser/util.go -->
# sources/user-network-fs/go-fuse/internal/vhostuser/util.go

## Purpose
Provides small utility functions for vhost-user setup: hugepage detection, feature mask composition, and the virtqueue eventfd read loop.

## Important APIs, Types, and Functions
`getFDHugepagesize`, `composeMask`, and `Virtq.readLoop` are the relevant functions.

## Control Flow
`readLoop` blocks on the kick fd, drains a batch from the virtqueue, clears writable buffers, logs optional debug data, calls the device handler in a goroutine per element, pushes completion, and notifies the guest.

## State and Persistence Behavior
The loop persists until its `readerControl.cancel` is closed or the kick fd read fails. It mutates request buffers and queue state but does not own durable storage.

## Dependencies and Integration Points
Depends on Linux fd/statfs behavior, `Virtq.popBatch`, `pushQueue`, `queueNotify`, and the FUSE protocol server callback used by virtiofs.

## Risks and Edge Cases
Spawning one goroutine per element can amplify load; handler panics can bypass completion; kick fd read errors terminate processing; `getFDHugepagesize` is Linux-specific behavior in a generic internal package.

## Test Signals
End-to-end virtiofs tests cover loop liveness. Race tests should toggle control-plane setup while kicks arrive and assert no goroutine or fd leak after disable/close.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/vhostuser/util.go -->
