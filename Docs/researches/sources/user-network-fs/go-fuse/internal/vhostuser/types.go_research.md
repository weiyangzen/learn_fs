<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/vhostuser/types.go -->
# sources/user-network-fs/go-fuse/internal/vhostuser/types.go

## Purpose
Defines vhost-user and virtio split-ring constants, request IDs, wire payload structs, feature-name decoding, and debug stringers.

## Important APIs, Types, and Functions
Important items include protocol feature constants, virtio feature constants, `Header`, `VhostVringAddr`, `VhostVringState`, `VhostUserMemoryRegion`, descriptor/ring structs, and `inFDCount`.

## Control Flow
There is no runtime protocol logic beyond formatting and mask composition support; `Server` casts payload bytes to these structs with `unsafe.Pointer` and uses decode maps for debug logging.

## State and Persistence Behavior
Struct values mirror wire messages and shared-memory ring layouts. They are transient except when copied into `Device`, `Ring`, or `Virtq` state.

## Dependencies and Integration Points
All vhost-user control handling depends on this file. It must stay ABI-compatible with QEMU/Linux headers and with the little-endian shared-memory expectations documented in `server.go`.

## Risks and Edge Cases
Unsafe struct casting is sensitive to padding, host endianness, and field width. Some constants are present without implementation, which can mislead future feature negotiation changes.

## Test Signals
Builds and QEMU negotiation provide coverage. ABI tests should check `unsafe.Sizeof` values, stringer output for masks, fd-count expectations, and request IDs against upstream vhost-user headers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/vhostuser/types.go -->
