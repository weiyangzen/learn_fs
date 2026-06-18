# File Research: sources/os/linux/linux-stable/fs/ext4/block_validity.c

## Purpose

Tracks ext4 filesystem metadata block ranges that must not be used as ordinary file or directory data blocks.

## Main Responsibilities

- Maintains an RCU-protected red-black tree of system zones.
- Adds and merges metadata block ranges.
- Builds the system-zone tree at mount/remount time.
- Releases the tree safely after RCU grace period.
- Validates inode block mappings and indirect block references against system zones.

## Key Data Structures

- `struct ext4_system_zone`: rbtree node containing start block, block count, and owning inode number.
- `ext4_system_zone_cachep`: slab cache for system-zone nodes.
- `struct ext4_system_blocks`: referenced through `sbi->s_system_blks`.

## Key Operations

- `ext4_init_system_zone()` and `ext4_exit_system_zone()` manage the slab cache.
- `add_system_zone()` inserts a non-overlapping metadata range and merges adjacent ranges with the same inode owner.
- `ext4_protect_reserved_inode()` maps blocks of special reserved inodes, such as the journal inode, and adds them as protected ranges.
- `ext4_setup_system_zone()` builds a complete tree from base metadata, block bitmaps, inode bitmaps, inode tables, and journal inode blocks, then publishes it with `rcu_assign_pointer()`.
- `ext4_release_system_zone()` clears the published pointer and frees the old tree after RCU grace period.
- `ext4_sb_block_valid()` rejects out-of-range blocks and blocks overlapping system zones, except when the overlapping zone belongs to the same inode.
- `ext4_inode_block_valid()` wraps superblock validation for an inode.
- `ext4_check_blockref()` scans 32-bit block references and reports `EFSCORRUPTED` if any reference targets invalid metadata space.

## Dependencies

- Includes VFS, namei, quota, buffer heads, swap, pagemap, blkdev, slab, and `ext4.h`.
- Uses ext4 group descriptor, metadata layout, block mapping, inode loading, and error-reporting helpers.

## Research Notes

This file is a mount-time metadata protection layer. It prevents corrupt or malicious metadata from causing ext4 to treat core filesystem structures as file data. The RCU swap pattern lets remount change block validity settings without racing readers.
