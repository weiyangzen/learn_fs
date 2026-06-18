# File Research: sources/os/bsd/netbsd-src/lib/libbz2/Makefile

Builds the in-tree bzip2 library.

Key behavior:
- Enables fortification by default.
- Builds `LIB=bz2` from the external BSD bzip2 distribution sources.
- Installs `bzlib.h` to `/usr/include`.
- Disables implicit-fallthrough warnings for the library.
- On SH3 with GCC, disables loop optimization for `blocksort.c` due to a known miscompilation.
- Installs `manual.html` under reference documentation when `MKSHARE != no`.

Dependencies:
- `${NETBSDSRCDIR}/external/bsd/bzip2/dist`.
- NetBSD info and library make infrastructure.
