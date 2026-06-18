# File Research: sources/local-fs/mtd-utils/ubi-utils/libubi.c

## Role
libubi implementation: userspace wrapper around UBI sysfs metadata and UBI ioctls.

## Main Behavior
- Builds sysfs path templates for UBI devices and volumes under `/sys/class/ubi`.
- Reads sysfs numeric/string files with validation helpers.
- Converts UBI device/volume character nodes to device and volume numbers by matching major/minor values.
- Opens/closes library descriptors and checks UBI version compatibility.
- Implements attach/detach/remove through UBI control ioctls.
- Implements volume create/remove/rename/resize through UBI device ioctls.
- Implements device and volume info lookup from sysfs.
- Implements volume block create/remove, update start, atomic LEB change, property set, LEB unmap, and mapped check.

## Interfaces And Dependencies
- Implements `include/libubi.h`.
- Uses path constants from `libubi_int.h`.
- Uses `common.h` diagnostics and kernel UBI ioctl structures.

## Notes
- Assumes the old `/sys/class/ubi/ubiX_Y` layout, as documented in `libubi_int.h`.
- `ubi_attach` uses a two-step probe to detect whether the kernel supports `max_beb_per1024`.
- Several parameters are intentionally unused and silenced via assignments like `desc = desc`.
