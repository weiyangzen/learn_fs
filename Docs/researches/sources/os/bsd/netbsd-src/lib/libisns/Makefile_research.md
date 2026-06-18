# File Research: sources/os/bsd/netbsd-src/lib/libisns/Makefile

Build file for NetBSD `libisns`.

It builds `isns` from core, PDU, socket I/O, task, thread, utility, and file I/O sources. Installs `isns.h` and `isns_defs.h` to `/usr/include`, links with pthread, sets warning level 5, and suppresses string truncation warnings for `isns.c`.
