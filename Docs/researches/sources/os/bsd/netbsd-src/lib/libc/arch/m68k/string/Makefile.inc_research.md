# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/string/Makefile.inc

This make include selects m68k assembly implementations for common string and memory functions: compare, copy, zero, set, concatenate, length, bounded string operations, byte search, byte swap, and move/copy variants. It includes both historical BSD routines and C-library entry points such as `memcpy`, `memccpy`, `memmove`, `strchr`, and `strrchr`.

The file is important build metadata for libc performance and symbol coverage. Any mismatch between listed sources and available assembly files would surface as build or missing-symbol failures.
