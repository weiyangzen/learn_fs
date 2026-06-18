# File Research: sources/os/bsd/dragonflybsd/sys/sys/types.h

## Summary
Core DragonFly BSD scalar type definitions shared by kernel and userland.

## Main Responsibilities
- Defines BSD/System V compatibility aliases under visibility gates.
- Defines file, device, ID, time, size, socket, filesystem-count, disk-address, and fixed-point types.
- Defines kernel-only `cdev_t` and `uoff_t`.
- Provides userland `major`, `minor`, and `makedev` macros for `dev_t`.
- Pulls in fd-set/timeval, pthread, stdint, and kernel integer/machine types as appropriate.

## Important Behavior
Several typedefs are guarded by `_FOO_T_DECLARED` macros to coordinate with other public headers. Userland sees `dev_t` as a 32-bit value and kernel code uses `struct cdev *` via `cdev_t`.

## Risks
This header is highly order-sensitive because many other headers depend on the declaration guards. Device-number macros intentionally preserve DragonFly’s cookie-style minor encoding rather than a simple index split.
