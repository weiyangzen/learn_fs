# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/utilities.c

Provides ext2 fsck utility functions for prompting, buffer cache management, I/O, allocation, pathname reconstruction, signals, and generic fix decisions.

Key utilities:
- `ftypeok` validates supported inode file types.
- `reply` implements interactive yes/no/force-yes prompting; preen mode treats reaching `reply` as an internal error.
- `bufinit`, `getdatablk`, `getblk`, and `flush` implement a small LRU-style metadata buffer cache.
- `bread` and `bwrite` perform sector-aligned reads/writes with detailed per-sector error reporting.
- `ckfini` flushes buffers, optionally updates standard superblocks, marks clean filesystems, prints cache stats, and closes fds.
- `allocblk` and `freeblk` manage block allocation map changes.
- `getpathname` reconstructs a pathname by walking parent directories and names.
- `catch`, `catchquit`, and `voidquit` handle interrupts and preen-mode quit behavior.
- `dofix` centralizes the decision to salvage/correct a detected inconsistency, with automatic salvage in preen mode.

This file supplies the operational machinery used throughout the ext2 checker’s pass code.
