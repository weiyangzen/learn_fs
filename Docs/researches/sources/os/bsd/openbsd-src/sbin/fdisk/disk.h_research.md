# File Research: sources/os/bsd/openbsd-src/sbin/fdisk/disk.h

## Purpose
Declares `fdisk` disk state and disk I/O helpers.

## Key Contents
- `struct disk` stores boot partition template, device name, fd, geometry, and sector count.
- Defines `BLOCKALIGNMENT` as 64 sectors, used for 32 KiB partition alignment.
- Declares `DISK_open()`, `DISK_printgeometry()`, `DISK_readbytes()`, and `DISK_writebytes()`.
- Exposes global `disk` and disklabel `dl`.

## Notes
The `BLOCKALIGNMENT` constant is shared by initialization and partition placement logic.
