# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/pass1.c

Implements ext2 fsck phase 1: block and inode size checking.

Major work:
- Marks reserved filesystem metadata blocks as used in `blockmap`: inode tables, block bitmaps, inode bitmaps, superblock/group descriptor copies, and pre-first-data blocks.
- Sequentially reads all inodes with the optimized inode buffer.
- Classifies each inode into unused, file, directory, duplicate/bad clear states, or unknown.
- Tracks file count, link counts, zero-link allocated inodes, last used inode, inode types, and cached directory inode metadata.
- Detects and optionally clears partially allocated or unknown-type inodes.
- Validates deleted-time fields on allocated inodes and can clear stale deletion times.
- Checks for impossible sizes, garbage block pointers after file end, bad file types, and incorrect block counts.

`pass1check` validates each block reference:
- Flags out-of-range blocks as bad.
- Adds new blocks to the allocation bitmap.
- Records duplicate blocks in the duplicate list.
- Enforces per-inode limits on reported bad and duplicate blocks.
- Counts visited blocks for later comparison with inode `e2di_nblock`.

This pass establishes the allocation and inode-state facts used by all later ext2 checks.
