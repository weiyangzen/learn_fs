# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/extern.h

Declares cross-file interfaces for `fsck_ext2fs`.

The prototypes cover:
- Directory repair and link-count adjustment.
- Block/inode allocation and freeing.
- Buffered device I/O.
- Inode cache and traversal.
- Directory entry scanning and validation.
- Pathname reconstruction and inode diagnostics.
- The five fsck passes and their block callbacks.
- Setup/cleanup and signal handlers.

This header is the internal linkage contract among ext2fs checker modules.
