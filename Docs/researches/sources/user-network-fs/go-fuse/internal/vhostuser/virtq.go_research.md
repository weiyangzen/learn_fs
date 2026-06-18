<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/vhostuser/virtq.go -->
# sources/user-network-fs/go-fuse/internal/vhostuser/virtq.go

## Purpose
Implements virtio split-ring data-plane operations for descriptor mapping, queue popping, used-ring publishing, notification, and queue lifecycle.

## Important APIs, Types, and Functions
Core APIs are `Virtq`, `Ring`, `MapRing`, `SetEnable`, `popBatch`, `popQueue`, `queueMapDesc`, `readVringEntry`, `pushQueue`, `queueNotify`, `SetVringAddr`, `Close`, and `VringNeedEvent`.

## Control Flow
On enable, `readLoop` consumes kicks. `popQueue` checks ring initialization, reads avail entries with barriers, maps descriptor chains including indirect descriptors, and increments in-use count. Completion writes used-ring entries, advances indexes, and signals the call fd when event-index logic requires it.

## State and Persistence Behavior
Queue state includes ring pointers into guest memory, eventfds, used/avail indexes, inflight placeholders, debug pointer, and goroutine control channels. It uses `mu` for vring state and device `dispatchMu` for control/data coordination.

## Dependencies and Integration Points
Depends on `deviceRegions` for guest address resolution, `barrier` memory fences for virtio ordering, Linux eventfd writes, and `types.go` ring structs.

## Risks and Edge Cases
Descriptor chains are guest-controlled and pointer-heavy; loops, mixed indirect chains, partial region reads, nil event pointers, or notification arithmetic mistakes can hang or corrupt queues. Packed rings and inflight recovery are not implemented.

## Test Signals
QEMU virtiofs traffic is the main signal. Unit tests should cover indirect descriptor bounds, multi-region buffers, event-index notification thresholds, queue disable while active, and malformed avail heads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/vhostuser/virtq.go -->
