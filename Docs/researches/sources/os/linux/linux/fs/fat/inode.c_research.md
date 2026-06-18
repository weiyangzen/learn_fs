# File Research: sources/os/linux/linux/fs/fat/inode.c

## Purpose
Core FAT filesystem implementation: address-space mapping, inode lifecycle, inode hashing, mount option parsing, superblock reading, root/inode construction, writeback, statfs, module initialization, and shared FAT mount context setup.

## Main Responsibilities
- Maps file blocks to FAT clusters for buffered, direct, and bmap I/O.
- Implements FAT address-space operations.
- Maintains inode caches keyed by on-disk directory entry position and directory start cluster.
- Builds VFS inodes from FAT directory entries.
- Reads and validates the BIOS Parameter Block and optional DOS 1.x defaults.
- Fills the superblock, loads NLS tables, creates root/FAT/FSINFO inodes.
- Parses and displays FAT/msdos/vfat mount options.
- Writes inode metadata back to directory entries.
- Initializes/destroys FAT inode and cluster-cache slabs.

## Key Interfaces
- `fat_add_cluster()`: allocates and appends one cluster.
- `fat_block_truncate_page()`: zeroes partial block tail on truncate.
- `fat_attach()` / `fat_detach()` / `fat_iget()`: manage on-disk-position inode hash.
- `fat_fill_inode()` / `fat_build_inode()`: populate or create VFS inodes from directory entries.
- `fat_sync_inode()`: writes one FAT inode synchronously.
- `fat_reconfigure()`: remount handling and dirty-state changes.
- `fat_parse_param()`: shared parser for core, msdos, and vfat mount options.
- `fat_fill_super()`: full FAT mount path.
- `fat_flush_inodes()`: optional flush behavior for mounts with `flush`.
- `fat_init_fs_context()` / `fat_free_fc()`: shared fs_context allocation and defaults.

## Important Behavior
The block mapping path uses `__fat_get_block()`. If the block already maps, it returns the physical block span. If creating and the block equals `mmu_private`, it allocates a cluster when needed, advances `mmu_private`, remaps, marks the buffer new, and detects corrupt file size/chain states.

`fat_direct_IO()` rejects direct writes that would extend beyond `mmu_private`, forcing buffered writes so holes can be zero-filled and allocation state updated correctly.

Inode identity is deliberately independent of disk position. `i_ino` is generated, while `i_pos` points to the directory entry and is used by FAT’s own hash. NFS nostale mode uses `i_pos` file handles and a directory hash by logical start cluster.

`fat_fill_inode()` distinguishes directory versus regular file setup, calculates directory size by walking to EOF, sets link count from subdirectory count, applies `showexec`, `sys_immutable`, attributes, timestamps, birth time, and rounded block count.

`fat_fill_super()` validates BPB fields, handles logical sector size changes, discovers FAT12/16/32 geometry, reads FAT32 FSINFO, validates cluster count, initializes locks/hash tables/FAT operations, loads NLS codepages, creates internal inodes, builds root, warns for discard without support, and marks the volume dirty on mount.

## Mount Options
Core options include uid/gid, umask/dmask/fmask, allow_utime, codepage, usefree, nocase, quiet, showexec, sys_immutable, flush, timezone/time_offset, errors policy, discard, NFS mode, and DOS 1.x floppy fallback. VFAT adds iocharset, shortname policy, utf8, unicode escaping, numtail, and rodir. MSDOS adds dots/dotsOK.

## Dependencies
This file is the hub for all FAT subsystem files. It calls directory helpers, FAT entry operations, cache/block mapping helpers, timestamp/error helpers, and exposes common functionality to msdos/vfat modules.

## Research Notes
The mount path has many compatibility accommodations: optional DOS 1.x static BPB, permissive first-FAT-entry media validation, FSINFO trust only with `usefree`, UTF-8 warnings, and read-only enforcement for `nfs=nostale_ro`.
