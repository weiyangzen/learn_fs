# File Research: sources/teaching/minix/minix/fs/isofs/stadir.c

This file implements stat and statvfs for isofs.

Entry points:
- `fs_stat(ino_nr, statbuf)`: copies cached inode `struct stat`.
- `fs_statvfs(st)`: reports block sizing, total volume blocks, and name max.

Behavior:
- Read-only filesystem statistics set `ST_NOTRUNC`.
- `f_bsize`, `f_frsize`, and `f_iosize` are all the ISO logical block size.
- `f_blocks` comes from the primary volume descriptor’s volume space size.
- Does not report free block/inode fields, consistent with read-only ISO media.
