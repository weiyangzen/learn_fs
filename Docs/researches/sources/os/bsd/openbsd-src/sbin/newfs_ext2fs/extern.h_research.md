# File Research: sources/os/bsd/openbsd-src/sbin/newfs_ext2fs/extern.h

Purpose: Shared declarations between `newfs_ext2fs.c` and `mke2fs.c`.

Definitions:
- Defines `EXT2_LOG_MAXBSIZE` and `EXT2_MAXBSIZE`, noted as belonging in ext2fs headers.
- Provides `nitems()` if unavailable.

API:
- Declares `void mke2fs(const char *, int);`.

Shared globals:
- Declares front-end-populated settings: `Nflag`, `Oflag`, verbosity, filesystem size, inode size, sector size, fragment size, block size, minfree, inode count/density, and volume name.
