# File Research: sources/os/bsd/netbsd-src/lib/libperfuse/Makefile

Read completely: 19 lines.

This builds `libperfuse` from `perfuse.c`, `ops.c`, `subr.c`, and `debug.c`, links against `libpuffs`, installs `perfuse.h`, and installs `libperfuse.3`.

It defines `_KERNTYPES`, includes the local directory and `libpuffs`, sets warnings to 5, and provides an optional debug flags variable.

Security/reliability notes: build-only file. `_KERNTYPES` affects kernel type visibility in userland headers.
