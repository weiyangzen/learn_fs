# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ffs/Makefile

Builds the `fsck_ffs` checker.

Sources:
- FFS-specific checker files: `dir.c`, `inode.c`, `main.c`, `pass1.c`, `pass1b.c`, `pass2.c`, `pass3.c`, `pass4.c`, `pass5.c`, `setup.c`, `utilities.c`.
- Shared generic `fsutil.c`.
- Kernel FFS support sources: `ffs_subr.c`, `ffs_tables.c`.

Build details:
- Adds kernel FFS and shared fsck source paths.
- Adds `../fsck` to include path.
- Links with `libutil`.
