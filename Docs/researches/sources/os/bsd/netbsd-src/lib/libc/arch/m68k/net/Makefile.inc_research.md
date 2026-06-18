# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/net/Makefile.inc

This make include adds m68k assembly byte-order conversion sources: `htonl.S`, `htons.S`, `ntohl.S`, and `ntohs.S`. It is consumed by the libc architecture build to select machine-specific network-order routines.

The file contains no logic beyond source selection, so the main dependency is the existence and correctness of the named assembly files in the same architecture tree.
