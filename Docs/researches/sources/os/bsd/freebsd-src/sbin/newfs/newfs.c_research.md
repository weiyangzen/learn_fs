# File Research: sources/os/bsd/freebsd-src/sbin/newfs/newfs.c

Command-line frontend for building UFS filesystems. It parses `newfs` options, resolves device or file-backed targets, obtains sector/media size and optional disklabel data, normalizes defaults, then calls `mkfs()`.

Key behaviors:
- Defines all global configuration consumed by `mkfs.c`, including UFS version, block sizes, fragment sizes, inode density, minfree, soft updates, journal flags, volume label, erase/TRIM, and regression/fault-injection flags.
- Accepts both character devices and regular files; file mode can use a BSD label partition offset via `-p`.
- Uses `ufs_disk_fillout_blank()` and `ufs_disk_write()` for device setup unless operating on a plain file.
- Applies default soft updates for UFS2 unless gjournal is requested.
- After `mkfs()`, optionally executes `tunefs -j enable` for soft updates journaling.

Important dependencies:
- `libufs`, `libutil` `expand_number`, disk ioctls `DIOCGSECTORSIZE` and `DIOCGMEDIASIZE`, and BSD disklabel helpers.
- `mkfs()` from `mkfs.c`.

Research notes:
- This file owns user input validation; downstream geometry assumptions in `mkfs.c` rely on this normalization.
- `-R` is important for reproducible filesystem images in the included regression scripts.
