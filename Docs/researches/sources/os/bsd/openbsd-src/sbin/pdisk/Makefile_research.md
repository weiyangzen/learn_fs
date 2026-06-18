# File Research: sources/os/bsd/openbsd-src/sbin/pdisk/Makefile

Purpose: Builds `pdisk`, the Apple partition map utility, only on macppc.

Build details:
- Conditional on `${MACHINE} == "macppc"`.
- `PROG=pdisk`.
- Sources are `dump.c`, `file_media.c`, `io.c`, `partition_map.c`, and `pdisk.c`.
- Adds `-Wall` and links with `libutil`.
- On other machines, sets `NOPROG=yes`.
- Installs `pdisk.8` under `MANSUBDIR=macppc`.
