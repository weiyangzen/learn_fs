# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/Makefile.inc

OpenBSD make fragment for libunbound service modules.

Contents:
- Adds `${.CURDIR}/libunbound/services` to `.PATH`.
- Adds service sources: `authzone.c`, `listen_dnsport.c`, `localzone.c`, `mesh.c`, `modstack.c`, `outbound_list.c`, `outside_network.c`, `rpz.c`, and `view.c`.

Role:
- Includes resolver service-layer implementation files in the unwind/libunbound build.
