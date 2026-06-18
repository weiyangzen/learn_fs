# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/net/htonl.c

This C file implements `htonl` for little-endian SH3 builds only. It uses inline assembly `swap.b`, `swap.w`, and `swap.b` to reverse byte order of a 32-bit value, returning the network-order result.

On big-endian builds the function body is not compiled from this file, implying a generic identity or alternate implementation is used elsewhere. The file’s core dependency is SH swap instruction semantics.
