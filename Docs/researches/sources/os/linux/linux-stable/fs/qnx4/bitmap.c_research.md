# File Research: sources/os/linux/linux-stable/fs/qnx4/bitmap.c

## Summary
Provides QNX4 free-block counting for `statfs`.

## Main Responsibilities
- Locate bitmap blocks through the cached `.bitmap` inode in `qnx4_sb_info`.
- Read bitmap blocks and count zero bits as free blocks.
- Stop counting on I/O error and return the count accumulated so far.

## Key Interfaces
- `qnx4_count_free_blocks()` is called by `qnx4_statfs()`.

## Important Behavior
The function interprets each byte of bitmap data as eight block bits and computes free space as total bits minus `memweight()` of set bits.

## Cross-File Interactions
`inode.c` caches the `.bitmap` inode during root validation and uses this helper in `qnx4_statfs()`.
