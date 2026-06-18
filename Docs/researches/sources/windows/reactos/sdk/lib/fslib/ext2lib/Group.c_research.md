# File Research: sources/windows/reactos/sdk/lib/fslib/ext2lib/Group.c

This file handles ext2 block group descriptor support and sparse-superblock placement.

Core responsibilities:
- `test_root` checks whether a group number is a power of a supplied base.
- `ext2_bg_has_super` implements ext2 sparse-superblock rules: all groups if sparse-super is disabled, otherwise group 0/1 and powers of 3, 5, or 7.
- `ext2_allocate_group_desc` allocates and zeroes the group descriptor table.
- `ext2_free_group_desc` frees the descriptor allocation and clears the pointer.

Risk points:
- Allocation size is `desc_blocks * blocksize`; callers must initialize those fields first.
- Sparse-super logic follows classic ext2 behavior and does not account for ext4-style metadata features.
