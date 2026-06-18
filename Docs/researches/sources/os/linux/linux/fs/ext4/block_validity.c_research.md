# File Research: sources/os/linux/linux/fs/ext4/block_validity.c

## Purpose
Tracks filesystem metadata block ranges so ext4 can reject file mappings that overlap protected system zones.

## Main Responsibilities
- Maintains an RCU-protected red-black tree of `ext4_system_zone` ranges.
- `ext4_setup_system_zone()` builds the tree from each group’s base metadata, block bitmap, inode bitmap, inode table, and internal journal inode blocks when present.
- `add_system_zone()` inserts non-overlapping ranges and merges adjacent ranges belonging to the same inode marker.
- `ext4_release_system_zone()` swaps out the tree and frees it after an RCU grace period.
- `ext4_sb_block_valid()` checks a block range against filesystem bounds and system-zone overlap.
- `ext4_inode_block_valid()` applies the check for an inode.
- `ext4_check_blockref()` validates arrays of block references and reports corrupt references.

## Integration Points
Uses ext4 group metadata helpers, inode block mapping, journal inode awareness, RCU, rbtrees, slab cache lifecycle, and ext4 error reporting.

## Risks and Edge Cases
Overlap while building the system zone is treated as corruption. RCU is required because block validation can run concurrently with remount changes that enable/disable block validity. Journal inode blocks are allowed for the journal inode itself but protected from regular file mappings.
