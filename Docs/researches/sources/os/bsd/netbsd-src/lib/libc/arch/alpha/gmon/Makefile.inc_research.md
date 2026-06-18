# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/gmon/Makefile.inc

Alpha gmon build fragment.

Key behavior:
- Adds `_mcount.S` for profiling instrumentation support.

Dependencies:
- Alpha profiling assembly implementation.
