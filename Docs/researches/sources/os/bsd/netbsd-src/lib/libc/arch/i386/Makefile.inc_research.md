# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/i386/Makefile.inc

This i386 libc make fragment adds `__sigtramp2.S` outside rumprun builds and includes the architecture directory with `CPPFLAGS+= -I.`.
