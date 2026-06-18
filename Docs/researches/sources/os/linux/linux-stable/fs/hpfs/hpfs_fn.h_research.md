# File Research: sources/os/linux/linux-stable/fs/hpfs/hpfs_fn.h

## Purpose

Central internal HPFS header for runtime state structures, inline helpers, prototypes, time conversion, and locking.

## Main Contents

Defines `hpfs_inode_info`, `hpfs_sb_info`, `quad_buffer_head`, dirent/EA inline accessors, bitmap bit testing, subsystem prototypes, and global lock helpers. It also defines allocation/read-ahead constants and HPFS-specific error aliases.

## Control Flow And State

`hpfs_sb_info` holds the global HPFS mutex, mount options, bitmap directory, code-page table, hotfix map, and allocation counters. `hpfs_inode_info` caches allocation lookup state, directory root dnode, EA metadata flags, dirty state, and active readdir positions. Locking is intentionally filesystem-wide via `hpfs_lock()`.

## Dependencies

Includes Linux mutex, pagemap, buffer-head, slab, signal, block-device, unaligned helpers, plus `hpfs.h`.

## Risks

All HPFS implementation files share this header. The global-lock model simplifies correctness but limits concurrency. Inline dirent and EA accessors assume validated on-disk lengths; misuse on corrupt data can produce invalid pointer arithmetic.
