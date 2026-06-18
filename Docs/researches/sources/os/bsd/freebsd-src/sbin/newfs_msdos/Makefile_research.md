# File Research: sources/os/bsd/freebsd-src/sbin/newfs_msdos/Makefile

Builds the `newfs_msdos` utility.

Key contents:
- Program: `newfs_msdos`.
- Sources: `newfs_msdos.c` and `mkfs_msdos.c`.
- Manual page: `newfs_msdos.8`.
- Package: `runtime`.
- Enables tests via `HAS_TESTS` and `SUBDIR.${MK_TESTS}+= tests`.
- Lowers warnings on ARM with a comment marking this as undesirable.

Research notes:
- The utility is split into CLI wrapper and reusable FAT filesystem construction engine.
