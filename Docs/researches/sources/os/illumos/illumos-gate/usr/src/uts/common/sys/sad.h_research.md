# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sad.h

## Role

`sad.h` defines the STREAMS Administrative Driver ABI for autopush configuration, versioned ioctl layout, device names, and kernel autopush cache interfaces.

## Ioctl Versioning

Only `SAD_GAP` and `SAD_SAP` are currently versioned, but the namespace reserves a 4-bit version and 4-bit command field. Userland defaults `AP_VERSION` to 0 unless explicitly defined; the kernel defaults to latest version 1.

Ioctls:
- `SAD_SAP`: set autopush.
- `SAD_GAP`: get autopush.
- `SAD_VML`: validate module list.

Devices are `/dev/sad/user` and `/dev/sad/admin`.

## Autopush Structures

`apcommon` carries command, major, minor, last minor, and number of modules. `apdata` adds an anchor position. `strapush` combines common data, a module-name list of up to `MAXAPUSH`, and versioned data when `AP_VERSION > 0`.

Commands are clear, one minor, range, and all minors.

## Kernel State

Kernel code gets ioctl state constants, version/command extraction macros, versioned structure lengths, `saddev`, `autopush`, and helper prototypes. Autopush cache operations are grouped by locking requirement: no `ss_sad_lock`, internally acquiring it, or requiring it already held.

Audit hooks for STREAMS messages and fd send/receive are declared.

## Research Notes

This is a versioned STREAMS admin ABI. `strapush` growth without breaking old binaries is the main design point, and autopush cache locking requirements are explicitly documented.
