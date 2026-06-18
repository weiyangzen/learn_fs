# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/locale/Makefile.inc

Read completely: 6 lines.

This makefile fragment adds compatibility locale sources to libc: `compat_setlocale1.c` and `compat_setlocale32.c`. It extends `.PATH` to machine-specific and generic compat locale directories and adds the current locale include path.

Security/reliability notes: build orchestration only.
