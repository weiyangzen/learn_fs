# File Research: sources/os/bsd/freebsd-src/sbin/growfs/Makefile

Builds the `growfs` utility.

Key contents:
- Includes `src.opts.mk`.
- Assigns package `ufs`.
- Builds `growfs` from `growfs.c`, with man page `growfs.8`.
- Optional `GFSDBG` adds `debug.c`, defines `FS_DEBUG`, and disables cast-alignment warnings.
- Links `ufs` and `util`.
- Declares tests and descends into `tests` when `MK_TESTS` is enabled.

This makefile keeps debug dumping out of normal builds unless explicitly requested.
