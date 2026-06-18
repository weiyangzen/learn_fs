# File Research: sources/os/linux/linux/fs/minix/bitmap.c

## Purpose
`bitmap.c` implements Minix filesystem block and inode bitmap operations plus raw inode-location helpers for Minix v1 and v2/v3 inode formats.

## Main Responsibilities
- Counts free bits in inode and zone bitmaps.
- Allocates and frees data blocks.
- Locates raw on-disk Minix v1 and v2/v3 inode records.
- Clears deleted inode metadata on disk.
- Allocates and frees inode numbers.
- Initializes newly allocated VFS inodes and inserts them into the inode hash.

## Key Functions
- `count_free()`: counts zero bits across bitmap buffer heads.
- `minix_free_block()`: validates a block against data-zone bounds, clears the corresponding zone bitmap bit, and marks the bitmap buffer dirty.
- `minix_new_block()`: scans zone bitmap buffers for a zero bit, sets it, marks dirty, converts the bit index to an on-disk zone number, and returns 0 on failure.
- `minix_count_free_blocks()`: counts free zones and shifts by `s_log_zone_size`.
- `minix_V1_raw_inode()` / `minix_V2_raw_inode()`: validate inode number, compute containing disk block after boot/super/imap/zmap blocks, read it, and return the raw inode pointer.
- `minix_clear_inode()`: zeros link count and mode in the raw on-disk inode for deletion.
- `minix_free_inode()`: validates inode number, clears the on-disk inode, clears the inode bitmap bit, and marks dirty.
- `minix_new_inode()`: allocates a VFS inode, finds/sets a free inode bitmap bit, initializes owner/timestamps/block count/private Minix data, inserts into inode hash, and marks dirty.
- `minix_count_free_inodes()`: counts zero bits in inode maps.

## Integration Points
- Uses `struct minix_sb_info` fields populated by Minix superblock code.
- Uses Minix endian-aware bit helpers such as `minix_find_first_zero_bit()`, `minix_test_and_set_bit()`, and `minix_test_and_clear_bit()`.
- Uses buffer-head I/O (`sb_bread`, `mark_buffer_dirty`, `brelse`).
- Called by Minix inode/name/block mapping operations elsewhere in the driver.

## Concurrency and Lifetime Notes
- A single static `bitmap_lock` serializes bitmap bit scanning and bit updates.
- Buffer heads are marked dirty after bitmap or raw inode modifications.
- `minix_new_inode()` releases the allocated VFS inode with `iput()` on allocation/validation failures after `new_inode()`.

## Risks and Edge Cases
- Block and inode bounds checks print warnings and return rather than repairing corruption.
- The bit arithmetic reserves bit/inode zero according to Minix layout conventions.
- `minix_new_block()` can find a free bit whose computed zone is outside filesystem bounds; it breaks and returns 0.
- `minix_new_inode()` returns `-EFSCORRUPTED` if the selected bit maps to inode 0 or beyond `s_ninodes`.
