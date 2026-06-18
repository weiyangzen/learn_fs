# File Research: sources/local-fs/mtd-utils/ubi-utils/libubi_int.h

## Role
Internal libubi sysfs path schema and descriptor definition.

## Main Contents
- Defines UBI sysfs directory names, device file names, volume file names, and format patterns.
- Defines `struct libubi`, which stores allocated full path templates for control, device, and volume sysfs files.

## Interfaces And Dependencies
- Private to `libubi.c`.

## Notes
- Comment explicitly notes older and newer kernel sysfs layouts and states libubi assumes the old layout.
- `struct libubi` owns many heap-allocated path strings freed by `libubi_close`.
