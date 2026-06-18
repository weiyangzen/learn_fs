# File Research: sources/os/linux/linux-stable/fs/fat/fat.h

This header defines the private FAT filesystem ABI shared across the FAT core, directory code, namei implementations, NFS export code, tests, and module setup.

Key data structures:
- `struct fat_mount_options` stores mount behavior: ownership, masks, codepage/iocharset, timestamp offset, shortname policy, error policy, NFS mode, and feature flags such as `flush`, `discard`, `rodir`, `utf8`, and `unicode_xlate`.
- `struct msdos_sb_info` is the in-core superblock: geometry, FAT layout, root directory layout, FSINFO state, locks, free-cluster cache, NLS tables, inode/dir hash tables, FAT entry operations, and dirty-state tracking.
- `struct msdos_inode_info` extends VFS inode state with cluster-cache LRU state, first/logical cluster, on-disk directory-entry position, truncate lock, creation time, and metadata buffer tracking.
- `struct fat_slot_info` describes a matched or inserted directory entry range.
- `struct fat_entry` represents a FAT table entry cursor, including variant-specific entry pointers and buffer_heads.

Important inline helpers:
- `MSDOS_SB()` and `MSDOS_I()` convert VFS objects to FAT-private state.
- `is_fat12()`, `is_fat16()`, `is_fat32()`, and `max_fat()` classify FAT variants.
- `fat_mode_can_hold_ro()`, `fat_make_mode()`, `fat_make_attrs()`, and `fat_save_attrs()` translate between DOS attribute bits and Unix mode semantics.
- `fat_checksum()` computes the VFAT long-name alias checksum.
- `fat_clus_to_blknr()`, `fat_get_blknr_offset()`, `fat_get_start()`, and `fat_set_start()` encode/decode on-disk locations and cluster numbers.
- `fat16_towchar()` and `fatwchar_to16()` handle endian-safe UTF-16 slot conversion.
- `fatent_init()`, `fatent_set_entry()`, `fatent_brelse()`, and `fat_valid_entry()` manage FAT entry cursors.

Exported interfaces:
- Declares cross-file functions for cluster caching, directory scanning/mutation, FAT entry access/allocation/free/trim, regular file operations, inode/superblock lifecycle, error reporting, time conversion, NFS export operations, and buffer synchronization.

Research relevance:
- This file is the central contract for the FAT implementation. It shows which state is global per superblock, which is per inode, and which helpers form the boundaries between cache, directory, allocation, file, inode, and namespace layers.
