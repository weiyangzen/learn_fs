# File Research: sources/teaching/minix/minix/fs/isofs/read.c

This file implements isofs file reads and directory enumeration.

Entry points:
- `fs_read(ino_nr, data, bytes, pos, call)`: reads file data from extents into fsdriver output.
- `fs_getdents(ino_nr, data, bytes, pos)`: emits cached directory entries.

Read behavior:
- Rejects missing inode.
- Returns EOF when position is past file size.
- Clamps read length to file size.
- Splits reads by logical block size.
- Uses `read_extent_block()` and `fsdriver_copyout()`.

Getdents behavior:
- Loads directory contents through `read_directory()`.
- Uses `fsdriver_dentry_add()` with inode number, cached name, and `IFTODT(mode)`.
- Updates `*pos` to the next directory index after successful finish.

Notable risk:
- `read_extent_block(&i_node->extent, pos)` receives a byte position; utility semantics must match that use.
