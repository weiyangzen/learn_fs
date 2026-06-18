# File Research: sources/teaching/minix/minix/fs/mfs/super.h

`super.h` defines the MFS superblock structure and documents the on-disk layout: boot block, superblock at 1KB, inode bitmap, zone bitmap, inode table, alignment padding, and data zones. The struct begins with on-disk fields such as inode count, map sizes, first data zone, zone size shift, flags, maximum file size, zone count, magic, block size, and disk format sub-version.

Fields after `s_disk_version` are memory-only and must remain coordinated with `LAST_ONDISK_FIELD` in `super.c`. These include derived counts, first data zone, device, read-only/native/version flags, direct/indirect counts, and bitmap search cursors.

The file defines `IMAP` and `ZMAP` bitmap selectors, the clean flag `MFSFLAG_CLEAN`, and `MFSFLAG_MANDATORY_MASK` for future incompatible features that older MFS implementations must reject.
