# File Research: sources/os/bsd/freebsd-src/sbin/newfs_msdos/newfs_msdos.c

Command-line wrapper for creating FAT filesystems. It parses options into `struct msdos_options`, resolves target path and optional disk type, then calls `mkfs_msdos()`.

Key behaviors:
- Parses FAT type, image creation size, bootstrap path, OEM string, volume label/ID, timestamp, block/sector/cluster sizing, geometry, FAT count, media descriptor, reserved sectors, hidden sectors, and dry-run mode.
- Supports suffix multipliers for offsets and create size: sectors, KB, MB, GB.
- If not creating a regular image and the target has no slash, prefixes `/dev/`.
- Enforces `-A` alignment incompatibility with explicit reserved-sector count.
- Generates usage output from `ALLOPTS`.

Research notes:
- CLI validation is mostly range based; structural FAT consistency is checked in `mkfs_msdos.c`.
