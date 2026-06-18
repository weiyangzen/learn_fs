# File Research: sources/teaching/minix/minix/fs/ext2/stadir.c

This file implements stat and statvfs for ext2.

Entry points:
- `fs_stat(ino_nr, statbuf)`: opens inode, updates pending times, fills POSIX stat fields, then releases inode.
- `fs_statvfs(st)`: fills filesystem-wide block, inode, free-space, and name-length data.

Important fields:
- Special file device number is reported from `i_block[0]`.
- `st_blocks` uses ext2 `i_blocks`, which counts 512-byte units.
- `f_bavail` subtracts reserved blocks from total free blocks.
- `ST_NOTRUNC` is set in `f_flag`.

Dependencies:
- Uses `get_inode`, `put_inode`, `update_times`, and `get_super`.
