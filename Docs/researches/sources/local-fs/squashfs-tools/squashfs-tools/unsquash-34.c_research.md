# File Research: sources/local-fs/squashfs-tools/squashfs-tools/unsquash-34.c

This helper file provides utilities shared by Squashfs 3.x and 4.x readers.

Key functions:
- `alloc_index_table`: reusable static allocation for 64-bit filesystem index tables.
- `inumber_lookup`: tracks visited directory inode numbers with an on-demand bit table.
- `free_inumber_table`: frees the visited-directory table.
- `lookup`: finds a previously extracted non-directory inode pathname by inode number.
- `insert_lookup`: records a pathname for an inode number.
- `free_lookup_table`: frees the hardlink lookup table, optionally freeing stored pathnames.

Important behavior:
- The inode-number table prevents invalid multiple directory links and directory loops during extraction.
- The hardlink lookup table lets unsquashfs create hardlinks for repeated non-directory inode numbers.
- Both structures allocate index pages lazily so partial filesystem traversal does not allocate for every inode.

Dependency notes:
- Index/offset/bit sizing macros such as `INUMBER_INDEXES` and `LOOKUP_INDEXES` come from `unsquashfs.h`.
- `alloc_index_table(0)` frees its static buffer and is used by readers after table parsing.
