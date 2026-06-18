# File Research: sources/local-fs/mtd-utils/lib/libmtd.c

## Purpose
Provides the main libmtd implementation for discovering MTD devices, reading sysfs attributes, mapping device nodes to MTD numbers, and performing erase, lock, bad-block, read, write, OOB, image-write, and probe operations.

## Main Entry Points
- `libmtd_open()` builds sysfs path patterns under `/sys/class/mtd` and detects whether the kernel has usable MTD sysfs support.
- `libmtd_close()` releases path templates and descriptor state.
- `mtd_dev_present()`, `mtd_get_info()`, `mtd_get_dev_info1()`, and `mtd_get_dev_info()` expose inventory and per-device metadata.
- `mtd_lock()`, `mtd_unlock()`, `mtd_erase()`, `mtd_regioninfo()`, and `mtd_is_locked()` wrap MTD ioctls.
- `mtd_torture()`, `mtd_is_bad()`, and `mtd_mark_bad()` exercise or manage eraseblocks and NAND bad-block state.
- `mtd_read()`, `mtd_write()`, `mtd_read_oob()`, `mtd_write_oob()`, `mtd_write_img()`, and `mtd_probe_node()` implement data/OOB I/O and node validation.

## Control Flow and State
Sysfs-backed discovery reads per-device files such as `dev`, `name`, `type`, `erasesize`, `size`, `writesize`, `subpagesize`, `oobsize`, `numeraseregions`, and `flags`. If sysfs is not available, public inventory calls delegate to `libmtd_legacy.c`.

The descriptor caches whether 64-bit offset ioctls are supported. Erase and OOB helpers first try `MEMERASE64`, `MEMREADOOB64`, or `MEMWRITEOOB64` when support is unknown or known-present, then fall back to legacy 32-bit ioctls when the kernel reports unsupported operations.

## Dependencies
Depends on Linux MTD UAPI (`mtd/mtd-user.h`), `libmtd.h`, `common.h` logging/allocation helpers, sysfs, character-device metadata, and standard POSIX file APIs.

## Risks and Notes
`mtd_torture()` sets `err = 0` on success but returns `-1` unconditionally at the `out:` label, which makes a successful torture test report failure. `mtd_read()` loops until the requested length is read but passes the original buffer pointer and original length to every `read()`, so short reads can overwrite earlier data and over-count progress. The OOB fallback path logs some 64-bit ioctl failures but still proceeds to the legacy ioctl unless the fallback itself rejects the request.
