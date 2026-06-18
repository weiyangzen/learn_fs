# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/string/Makefile.inc

This HPPA string make fragment builds `bcmp.S`, `bzero.S`, and `ffs.S`. It documents that `strlcpy.S` exists but is not currently enabled because NetBSD does not let architectures supply it there and the implementation is untested.
