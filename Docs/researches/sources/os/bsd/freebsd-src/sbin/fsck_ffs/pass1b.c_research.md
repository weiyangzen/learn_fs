# File Research: sources/os/bsd/freebsd-src/sbin/fsck_ffs/pass1b.c

This file implements phase 1b, the duplicate-block owner rescan.

Key behavior:
- Runs only when pass 1 found duplicate blocks.
- Rescans allocated inodes in cylinder-group order.
- Uses `pass1bcheck()` to compare each referenced fragment against the duplicate list.
- Emits `blkerror(..., "DUP", ...)` for inodes owning duplicate blocks.
- Advances `duphead` until all unique duplicate blocks have been found, then stops and requests rerun.

Important interactions:
- Uses pass-1 inode state, `duplist`, and `muldup`.
- Uses `ckinode()` traversal and the sequential inode buffer.
- Sets `rerun` when duplicate discovery is complete or traversal stops early.
