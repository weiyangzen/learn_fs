# sources/user-network-fs/mergerfs/vendored/libfuse/lib/mount.hpp

## Purpose
`mount.hpp` selects the platform-specific kernel mount implementation for the vendored FUSE layer.

## Important APIs, Types, and Functions
On FreeBSD, NetBSD, OpenBSD, or DragonFly it includes `mount_bsd.h`. Otherwise it includes `mount_generic.h` and `mount_util.h`.

## Control Flow
All behavior is compile-time selection based on OS macros. There is no executable logic in this header.

## State and Persistence
No direct state exists. The included implementations manipulate process environment, fds, mount helpers, and mount table state.

## Dependencies and Integration Points
It is included by `mount.cpp`. `helper.cpp` relies on the selected implementation to provide `fuse_kern_mount` and `fuse_kern_unmount`.

## Risks
Because implementations live in headers, including this header from multiple source files could duplicate non-inline definitions. Portability depends on correct OS macro coverage.

## Test Signals
Compile on each supported OS family and verify the expected helper path is selected. Linux should include generic plus mtab utilities; BSD should include BSD-only mount code.
