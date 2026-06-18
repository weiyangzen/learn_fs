# sources/user-network-fs/libfuse/util/mount_service.h

## Purpose
Public internal header for the service-mount helper API.

## Important APIs, Types, And Functions
- Defines `MOUNT_SERVICE_FALLBACK_NEEDED` as `2`.
- Declares `mount_service_main`, `mount_service_subtype`, and `mount_service_present`.

## Control Flow
No executable flow; documents the fallback contract and subtype parsing behavior.

## State And Persistence
No state. Implementations may mount filesystems or inspect service sockets.

## Dependencies And Integration Points
Included by `fuservicemount.c` and `mount.fuse.c`; implementation depends on service socket naming and protocol definitions.

## Risks
The fallback return value is a positive process exit code, so callers must distinguish it from generic failure. `mount_service_subtype` returns a pointer into the caller-owned string.

## Test Signals
Validate fallback handling in `mount.fuse.c`, subtype pointer lifetime expectations, and service presence checks for `fuse.X`, `fuseblk.X`, and bare `X`.
