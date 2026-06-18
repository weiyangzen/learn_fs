# File Research: sources/teaching/minix/minix/fs/mfs/stadir.c

`stadir.c` implements `stat` and `statvfs` support. The private `estimate_blocks` helper estimates 512-byte block usage from file size, zone size, and the number of indirect and double-indirect blocks that would be needed. It intentionally does not read all indirect blocks, so holes are ignored and the result is conservative.

`fs_stat` opens the inode, materializes pending timestamps with `update_times`, fills mode, link count, owner, special-device number, size, timestamps, block size, and estimated block count, then releases the inode.

`fs_statvfs` reports filesystem totals from `superblock` and `used_zones`: total/free/available blocks, block and fragment size, I/O size, inode totals, free inode count via `count_free_bits(IMAP)`, and maximum filename length.
