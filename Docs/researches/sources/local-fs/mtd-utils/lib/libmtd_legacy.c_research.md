# File Research: sources/local-fs/mtd-utils/lib/libmtd_legacy.c

## Purpose
Implements libmtd compatibility for kernels without the modern MTD sysfs interface, using `/proc/mtd`, `/dev/mtd%d`, and older MTD ioctls.

## Main Entry Points
- `legacy_libmtd_open()` checks whether `/proc/mtd` exists.
- `legacy_dev_present()` scans `/proc/mtd` for an MTD number.
- `legacy_mtd_get_info()` counts devices and determines lowest/highest MTD numbers.
- `legacy_get_dev_info()` validates a character node, calls `MEMGETINFO`, probes bad-block support, fills `struct mtd_dev_info`, and obtains the name from `/proc/mtd`.
- `legacy_get_dev_info1()` formats `/dev/mtd%d` and delegates to `legacy_get_dev_info()`.

## Control Flow
`proc_parse_start()` reads `/proc/mtd` into a bounded buffer and verifies the header. `proc_parse_next()` walks one line at a time, extracting the device number, size, erase size, and quoted device name.

## Dependencies
Uses Linux MTD legacy ioctls, `common.h` helpers, POSIX file/stat APIs, and the internal libmtd declarations.

## Risks and Notes
The fallback cannot discover NAND subpage size, so it sets `subpage_size` equal to `min_io_size`. Some early returns from `/proc/mtd` scanning paths do not free the parser buffer before returning, causing small process-lifetime leaks in these short-lived utility contexts.
