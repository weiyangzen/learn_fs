# File Research: sources/os/bsd/freebsd-src/sbin/newfs_msdos/mkfs_msdos.c

Implements the FAT12/FAT16/FAT32 filesystem construction engine used by `newfs_msdos.c` and also conditionally by `makefs`.

Key behaviors:
- Defines packed on-disk boot-sector, BPB, FAT32 extended BPB, volume label, and directory-entry structures.
- Supports standard floppy formats and inferred geometry from devices, files, disklabels, floppies, or explicit options.
- Validates FAT type, bytes per sector, sectors per cluster, reserved sectors, FAT count, media descriptor, bootstrap file format, FAT32 info/backup sectors, and volume labels.
- Selects FAT12/16/32 automatically when not explicit, computes cluster count, FAT size, root directory sectors, and optional cluster alignment.
- Writes boot sector, BPB, FAT/FAT32 metadata, FSInfo sectors, root directory, and optional volume-label directory entry.
- Supports `no_create` dry-run mode and `create_size` regular-file image creation.
- Uses chunked writes based on `KERN_MAXPHYS`/`MAXPHYS`.
- Provides `SIGINFO` progress reporting while writing metadata sectors.

Important dependencies:
- FreeBSD disk, mount, floppy, disklabel, and sysctl APIs when not compiled as `MAKEFS`.
- `mkfs_msdos.h` option structure.
- Endian packing helpers implemented as local macros (`mk1`, `mk2`, `mk4`).

Research notes:
- This file is the authoritative FAT layout algorithm for FreeBSD `newfs_msdos`.
- The code carefully distinguishes FAT32-only options from FAT12/16-only root directory behavior.
- The `MAKEFS` mode changes device assumptions and requires `create_size`.
