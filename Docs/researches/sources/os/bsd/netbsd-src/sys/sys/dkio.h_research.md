# File Research: sources/os/bsd/netbsd-src/sys/sys/dkio.h

Defines disk-specific ioctl command numbers and cache/wedge/disk-info constants.

Key content:
- Disklabel ioctls: get/set/write default/clear label, plus old-label variants under compatibility.
- Raw format ioctls.
- Step/retry/write-label/keep-label/eject/lock controls.
- Bad-sector and cache controls.
- Cache flags: read/write enabled, changeable, save, FUA, DPO.
- `DKCACHE_COMBINE` macro.
- Wedge ioctls: add/get/delete/list/make/remove wedges.
- Strategy ioctls.
- Disk info dictionary ioctl.
- Test-unit-ready, sector size/media size, sector alignment ioctls.

Important behavior:
- Includes `sys/ioccom.h` and `prop/plistref.h`.
- Some numbers are reserved because of historical 6.99 discard ioctls.
- Kernel-only `DIOCGPARTINFO` and 32-bit compatibility adjustment are present.
