# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/pass1b.c

Implements ext2 fsck phase 1b: duplicate-block owner discovery.

Behavior:
- Runs only when phase 1 found duplicate blocks.
- Rescans all allocated inodes with `pass1bcheck`.
- For every block reference matching the duplicate list, reports a duplicate block error for that inode.
- Reorders/removes duplicate-list entries as duplicates are accounted for.
- Stops when all unique duplicate blocks through `muldup` have been found.

This phase identifies the first and later inode owners of duplicate blocks before phase 4 decides what to clear or free.
