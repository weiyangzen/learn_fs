# File Research: sources/os/linux/linux-stable/fs/minix/bitmap.c

## Summary
Minix block and inode bitmap management plus raw inode lookup helpers.

## Main APIs
`minix_free_block()`, `minix_new_block()`, `minix_count_free_blocks()`, `minix_V1_raw_inode()`, `minix_V2_raw_inode()`, `minix_free_inode()`, `minix_new_inode()`, and `minix_count_free_inodes()`.

## Behavior
Block bitmaps mark busy bits as set. Block allocation scans zone maps for the first zero bit, sets it, marks the buffer dirty, and translates bitmap position to disk zone. Freeing validates the data-zone range and clears the bit. Inode allocation scans inode maps, creates a VFS inode, assigns ownership/timestamps/number, clears Minix-private block pointers, inserts into inode hash, and marks dirty. Freeing clears link count and mode in the raw on-disk inode before clearing the bitmap bit.

## State and Synchronization
A global `bitmap_lock` protects bitmap bit operations. Bitmap buffers live in `minix_sb_info` as `s_imap` and `s_zmap`.

## Dependencies
Buffer heads, Minix superblock layout, endian-aware bitops through Minix helpers, VFS inode allocation, and raw V1/V2 inode formats.

## Risks
Allocation can set a bit that later maps outside valid inode/zone ranges, returning corruption/zero after dirtying the bitmap. Error handling relies on old-style printk warnings rather than recovery.
