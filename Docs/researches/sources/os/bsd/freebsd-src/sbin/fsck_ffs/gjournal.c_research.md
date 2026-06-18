# File Research: sources/os/bsd/freebsd-src/sbin/fsck_ffs/gjournal.c

This file implements the fast cleanup path for GEOM journaled UFS filesystems.

Key behavior:
- `gjournal_check(const char *filesys)` clears unreferenced inodes tracked by `fs_unrefs` and per-cylinder-group `cg_unrefs`.
- If no unreferenced inodes exist, it marks the superblock dirty and finishes clean immediately.
- Iterates cylinder groups, validates each with `check_cgmagic()`, and scans allocated inodes from `cg_inosused()`.
- Clears allocated regular files or directories with `di_nlink == 0`.
- Uses `clri()` and `freeblock()` to deallocate contents, clears the inode-used bitmap, decrements unref counters, updates `cg_irotor`, zeroes the dinode, and dirties inode/cylinder-group/superblock metadata.
- On cylinder group corruption, requests rerun and exits without marking clean.

Important interactions:
- Called from `main.c` when `FS_GJOURNAL` is set and a full fsck is not required.
- Uses normal fsck buffer, inode, and cylinder-group update routines, then finishes through `ckfini(1)`.
