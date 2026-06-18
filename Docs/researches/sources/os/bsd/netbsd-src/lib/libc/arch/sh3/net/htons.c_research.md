# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/net/htons.c

This C file implements `htons` for little-endian SH3 builds only. It uses inline assembly `swap.b` to swap the two bytes of a 16-bit value and returns the network-order result.

On big-endian builds this function is not emitted from this file. Correctness depends on compiler support for the SH inline assembly constraint and byte-swap instruction.
