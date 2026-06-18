# sources/user-network-fs/mergerfs/vendored/libfuse/lib/mount.cpp

## Purpose
`mount.cpp` is a tiny translation unit that includes `mount.hpp`, causing the platform-specific mount helper implementation to be compiled.

## Important APIs, Types, and Functions
The actual APIs are selected by `mount.hpp`: `fuse_kern_mount`, `fuse_kern_unmount`, and supporting helpers from either BSD or generic headers.

## Control Flow
There is no runtime control flow in this file beyond inclusion. Build-time platform macros choose which header implementation is compiled into this object.

## State and Persistence
No state is declared here. State belongs to the included helper implementation and the OS mount table/fds it manipulates.

## Dependencies and Integration Points
`helper.cpp` declares and calls `fuse_kern_mount`/`fuse_kern_unmount`; this file provides their definitions through the include model. It depends on `mount.hpp` and the platform macros it evaluates.

## Risks
Header-implemented functions can cause ODR/link surprises if included in more than one translation unit. Any platform macro mistake compiles the wrong mount path.

## Test Signals
Build on Linux and BSD targets, verify exactly one definition of mount helpers, and run mount/unmount smoke tests through `fuse_mount_common`.
