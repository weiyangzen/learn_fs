# File Research: sources/os/bsd/openbsd-src/sbin/fdisk/disk.c

## Purpose
Provides disk opening, geometry normalization, and sector/byte read-write helpers for `fdisk`.

## Key Behavior
- `DISK_open()` opens the target via `opendev()`, requires a character device, reads prototype disklabel with `DIOCGPDINFO`, and derives disk geometry.
- Honors user-supplied disk size (`-l`) or geometry (`-c/-h/-s`) when provided.
- Caps MBR-visible geometry to the first `UINT32_MAX` sectors.
- Converts boot partition size/offset from DEV_BSIZE blocks to disk sectors.
- `DISK_printgeometry()` prints disk geometry and total size in requested units.
- `readsectors()` and `writesectors()` perform whole-sector I/O using `lseek()`, `read()`, and `write()`.
- `DISK_readbytes()` reads enough sectors for an arbitrary byte-sized structure and copies the requested bytes.
- `DISK_writebytes()` preserves unaffected sector bytes by read-modify-writing whole sectors.

## Notes
This abstraction lets GPT/MBR code operate on structure-sized records while respecting physical/logical sector sizes.
