# File Research: sources/os/bsd/freebsd-src/sbin/fsck_ffs/Makefile

This is the FreeBSD build definition for the UFS/FFS filesystem checker.

Key behavior:
- Builds program `fsck_ffs` in package `ufs`.
- Installs hard links or command aliases for `fsck_ufs` and `fsck_4.2bsd`.
- Installs `fsck_ffs.8` with manpage links for the aliases.
- Builds the checker from directory, inode, pass, setup, soft-updates journal, gjournal, utility, and globals source files.
- Links against `libufs` and `libutil`.
- Adds the current directory to include search path and imports FFS kernel path sources through `.PATH: ${SRCTOP}/sys/ufs/ffs`.

Important interactions:
- The listed `SRCS` include files outside this research group, notably `suj.c` and `utilities.c`, which provide soft updates journal recovery and block device name handling.
