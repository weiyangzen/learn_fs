# File Research: sources/os/bsd/freebsd-src/sbin/fsck_ffs/ea.c

This file is intended to scan UFS2 external attribute blocks, but the actual scanner is compiled out.

Key behavior:
- `eascan(struct inodesc *, struct ufs2_dinode *)` currently returns `0` immediately.
- Disabled code would print external attribute block contents by reading `di_extb[0]` with `getdatablk()` and dumping bytes.

Important interactions:
- Called by pass 1 for UFS2 inodes with external attributes.
- Because the active implementation is a stub, this checker currently does not validate or repair EA payload structure here.
