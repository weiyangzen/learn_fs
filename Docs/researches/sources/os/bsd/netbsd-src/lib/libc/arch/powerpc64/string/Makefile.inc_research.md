# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/string/Makefile.inc

This make include adds PowerPC64 string assembly sources `bzero.S`, `ffs.S`, and `strlen.S`, while marking `memset.S` as not used. The local `bzero.S` provides both `bzero` and `memset`.

It is build metadata preventing duplicate `memset` objects while selecting optimized routines.
