# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/net/Makefile.inc

Read completely: 15 lines.

This makefile fragment adds `__cmsg_alignbytes.c`, `compat_ns_addr.c`, and `compat_ns_ntoa.c` to the compat network build. It also suppresses one lint warning in `compat_ns_ntoa.c` caused by lowercase-to-uppercase character arithmetic on unsigned character data.

Security/reliability notes: build-only; the lint suppression is narrowly targeted.
