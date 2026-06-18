# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ffs/extern.h

Declares internal interfaces shared by `fsck_ffs` modules.

The prototypes cover:
- Directory repair and link-count adjustment.
- Block/inode allocation and freeing.
- Buffered device and cylinder group I/O.
- Inode traversal and cache management.
- Directory scanning and validation.
- Pathname lookup and inode diagnostics.
- Pass entry points and pass block callbacks.
- Setup, cleanup, signal, and info handlers.

This is the FFS checker’s internal cross-module API.
