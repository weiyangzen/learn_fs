<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/vhostuser/deviceregion.go -->
# sources/user-network-fs/go-fuse/internal/vhostuser/deviceregion.go

## Purpose
Represents one shared-memory region supplied by QEMU for vhost-user guest memory.

## Important APIs, Types, and Functions
`deviceRegion`, `configure`, `Close`, `containsGuestAddr`, `FromDriverAddr`, and `String` wrap a `VhostUserMemoryRegion` plus the mmaped byte slice.

## Control Flow
`configure` validates driver-address overflow, maps the fd at `MmapOffset` for `MemorySize`, marks it `MADV_DONTDUMP`, and records the region. Translation methods later return byte-backed pointers or containment checks.

## State and Persistence Behavior
State is the mmaped `Data` slice and copied wire region metadata. `Close` unmaps the slice; the fd is owned by the caller and is closed in higher-level setup paths.

## Dependencies and Integration Points
Used by `deviceRegions.AddMemReg`, `Virtq.SetVringAddr`, and descriptor translation; depends on `syscall.Mmap`, `syscall.Munmap`, and `golang.org/x/sys/unix`.

## Risks and Edge Cases
Unsafe pointer conversion assumes the mmap remains live while vring and request buffers use it. Huge-page fds are rejected elsewhere; partial mappings or offset mistakes would corrupt guest address translation.

## Test Signals
QEMU virtiofs tests exercise normal mmap translation. Unit tests should cover overflow, offset mapping, out-of-range driver addresses, and unmap failure propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/vhostuser/deviceregion.go -->
