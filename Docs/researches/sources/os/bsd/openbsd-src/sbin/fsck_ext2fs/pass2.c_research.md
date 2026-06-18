# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/pass2.c

Implements ext2 fsck phase 2: pathname and directory entry checking.

Top-level flow:
- Ensures the root inode exists and is a directory, reallocating or fixing it when approved.
- Sorts cached directories by first block for efficient disk access.
- Checks each directory’s size, block alignment, and contents through `pass2check`.
- Performs a second pass over cached directories to verify or repair `..` parent links.
- Calls `propagate` to mark directories reachable from root.

Directory entry checks:
- Verifies and repairs `.` inode number and file type.
- Verifies, creates, or repairs `..` entries.
- Removes extra `.` and `..` entries after the first two slots.
- Removes entries pointing outside the inode range, unallocated inodes, or clear-pending inodes when approved.
- Detects extraneous hard links to directories.
- Records parent directory relationships.
- Decrements link-count accounting for every valid observed directory entry.
- Repairs ext2 directory file-type fields when the filesystem supports them.

This phase turns the raw directory cache from phase 1 into a connected directory graph and accurate observed link counts.
