# File Research: sources/os/linux/linux/fs/erofs/dir.c

Implements EROFS directory iteration.

Key behavior:
- Parses sorted fixed-block directory entries and variable-length names.
- `erofs_fill_dentries()` validates name offsets, name lengths, maximum name length, and block bounds before emitting entries.
- `erofs_readdir()` reads directory blocks through `erofs_bread()`, supports arbitrary starting positions, and performs optional directory readahead.
- Handles fatal signals with `-ERESTARTSYS`.
- Emits a synthetic `.` entry at end for directories with the on-disk dot entry omitted.
- Directory file operations include llseek, generic read, iterate, ioctl, compat ioctl, and generic leases.

Important interactions:
- Uses inode `dot_omitted` populated by `inode.c`.
- Directory readahead size comes from `EROFS_I_SB(dir)->dir_ra_bytes`.
