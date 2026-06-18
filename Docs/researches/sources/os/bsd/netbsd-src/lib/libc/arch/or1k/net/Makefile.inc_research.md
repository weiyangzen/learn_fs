# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/net/Makefile.inc

This make include adds C implementations of byte-order conversion functions: `htonl.c`, `htons.c`, `ntohl.c`, and `ntohs.c`. It has no local logic.

The file selects generic/simple C conversion sources for or1k rather than assembly. Build correctness depends on those sources matching or1k endian behavior.
