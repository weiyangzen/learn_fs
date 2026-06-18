<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/vhostuser/regions.go -->
# sources/user-network-fs/go-fuse/internal/vhostuser/regions.go

## Purpose
Maintains the collection of vhost-user memory regions and supplies lock-free address translation for queue readers.

## Important APIs, Types, and Functions
`deviceRegions`, `load`, `AddMemReg`, `FromDriverAddr`, `FromGuestAddr`, `findRegionByGuestAddr`, `Close`, and `GetMaxMemslots` are central.

## Control Flow
Writers add regions under `mu`, keep the slice sorted by guest address, and publish a new immutable slice with `atomic.Pointer`. Readers search the current slice without taking a lock.

## State and Persistence Behavior
Region slices are append-only after publication; old mapped regions remain alive. `Close` unmaps the currently loaded regions. There is no remove-region path despite protocol constants existing.

## Dependencies and Integration Points
Used by vhost-user control handling and virtqueue descriptor mapping. It depends on `deviceRegion.configure`, `getFDHugepagesize`, sorting, atomics, and unsafe byte slice exposure.

## Risks and Edge Cases
Overlap detection is absent, partial guest-range lookup only returns the first segment, and old slices could keep regions mapped after future remove support. Huge-page rejection may limit deployments.

## Test Signals
Tests should add multiple out-of-order regions, translate across boundaries, verify max-slot enforcement, reject huge pages, and run queue reads concurrently with `AddMemReg` under race detection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/vhostuser/regions.go -->
