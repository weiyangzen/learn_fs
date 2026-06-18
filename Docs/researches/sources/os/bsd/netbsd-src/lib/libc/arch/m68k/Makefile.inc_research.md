# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/Makefile.inc

This m68k libc make fragment adds signal, TLS, mmap, LWP-private, and `mremap` assembly support, includes local generated headers, and selects softfloat or hardfloat support. Hardfloat sources are included only when not building for `m68000`; alternate softfloat fenv handling is used when `MKLIBCSOFTFLOAT` is disabled.
