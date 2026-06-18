# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/string/Makefile.inc

This make include selects PowerPC string routines. It adds `bzero.S`, `ffs.S`, and `strlen.S`, and marks `memset.S` as not used.

The `bzero.S` source also defines `memset`, so suppressing a separate `memset.S` avoids duplicate symbol implementations. This file is source-selection glue for optimized string routines.
