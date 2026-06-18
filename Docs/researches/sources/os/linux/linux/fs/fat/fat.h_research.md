# File Research: sources/os/linux/linux/fs/fat/fat.h

## Purpose
Central private header for Linux FAT, msdos, and vfat implementation. It defines mount options, in-memory superblock and inode state, FAT entry abstractions, inline conversion helpers, and cross-file function declarations.

## Main Data Structures
- `struct fat_mount_options`: parsed mount policy such as uid/gid, masks, charset/codepage, shortname behavior, error policy, NFS mode, timestamp offset, flush/discard, VFAT options, and DOS compatibility flags.
- `struct msdos_sb_info`: in-core FAT superblock state including geometry, FAT layout, root directory layout, FSINFO state, locks, NLS tables, inode/dir hash tables, FAT operations, and mount options.
- `struct msdos_inode_info`: FAT-specific inode state including cluster-cache LRU, allocated size `mmu_private`, start/logical start clusters, attributes, on-disk directory-entry position, hash nodes, truncate lock, birth time, metadata buffer tracking, and embedded VFS inode.
- `struct fat_slot_info`: result container for directory entry searches and additions.
- `struct fat_entry`: abstraction for a FAT12/16/32 entry and its backing buffer heads.

## Key Inline Helpers
- `MSDOS_SB()` and `MSDOS_I()` cast VFS objects to FAT-specific state.
- `is_fat12()`, `is_fat16()`, `is_fat32()`, `max_fat()` classify FAT variant.
- `fat_make_mode()`, `fat_make_attrs()`, `fat_save_attrs()`, `fat_mode_can_hold_ro()` translate between DOS attributes and Unix mode bits.
- `fat_checksum()` computes VFAT long-name checksum over the 8.3 alias.
- `fat_clus_to_blknr()`, `fat_get_blknr_offset()`, `fat_get_start()`, `fat_set_start()` translate FAT directory and cluster fields.
- `fatent_init()`, `fatent_set_entry()`, `fatent_brelse()`, `fat_valid_entry()` manage FAT entry cursors.

## Exported Internal API
Declares the internal interfaces implemented by `cache.c`, `dir.c`, `fatent.c`, `file.c`, `inode.c`, `misc.c`, and `nfs.c`.

## Research Notes
This header is the coupling point for the FAT subsystem. It captures the main invariants: cluster numbers start at `FAT_START_ENT`, FAT32 start clusters use high and low directory-entry fields, `mmu_private` requires inode locking on allocation paths, and `i_pos` needs special care on 32-bit systems.
