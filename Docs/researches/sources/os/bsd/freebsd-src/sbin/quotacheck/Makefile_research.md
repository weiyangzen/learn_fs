# File Research: sources/os/bsd/freebsd-src/sbin/quotacheck/Makefile

Build file for the `quotacheck` utility.

Key elements:
- Builds program `quotacheck` in package `quotacheck`.
- Sources are `quotacheck.c`, `preen.c`, plus shared `fsutil.c` and `utilities.c` from fsck paths.
- Links `libutil` and `libufs`.
- Installs `quotacheck.8`.

Dependencies:
- `.PATH` pulls sources from sibling `fsck` and `fsck_ffs`.
- Uses `bsd.prog.mk`.
