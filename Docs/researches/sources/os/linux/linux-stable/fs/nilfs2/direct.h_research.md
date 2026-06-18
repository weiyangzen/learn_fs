# File Research: sources/os/linux/linux-stable/fs/nilfs2/direct.h

## Summary
Defines NILFS direct-map capacity and declares direct bmap initialization/conversion helpers.

## Main Contents
- `NILFS_DIRECT_NBLOCKS`.
- Direct key min/max macros.
- `nilfs_direct_init()`.
- `nilfs_direct_delete_and_convert()`.

## Important Details
The number of direct blocks is derived from the inode bmap payload size divided by 64-bit pointers, minus the direct-node header slot.

## Risks
Any change in `NILFS_BMAP_SIZE` or direct-node on-disk layout affects the maximum direct key range.
