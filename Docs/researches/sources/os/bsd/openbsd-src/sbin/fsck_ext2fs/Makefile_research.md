# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/Makefile

Builds the `fsck_ext2fs` checker.

Sources:
- Ext2-specific fsck passes and helpers: `dir.c`, `inode.c`, `main.c`, `pass1.c`, `pass1b.c`, `pass2.c`, `pass3.c`, `pass4.c`, `pass5.c`, `setup.c`, `utilities.c`.
- Shared generic fsck utility source: `fsutil.c`.
- Kernel ext2 byte-swap support: `ext2fs_bswap.c`.

Build details:
- Adds search paths for kernel ext2fs sources and shared fsck sources.
- Adds `../fsck` to include path.
- Links with `libutil`.
