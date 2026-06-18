# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/net/Makefile.inc

This i386 net make fragment does not add ordinary sources because byte-swap routines come from shared assembler files. It registers lint stub sources for `htonl`, `htons`, `ntohl`, and `ntohs`, adding them to `LSRCS`, `DPSRCS`, and `CLEANFILES`.
