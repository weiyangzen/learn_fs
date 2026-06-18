# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/gdtoa/Makefile.inc

This HPPA gdtoa make fragment adds `strtof.c`. It relies on HPPA-specific arithmetic and NaN headers to describe floating-point layout.

The file is build plumbing only; the local format headers carry the conversion-sensitive behavior.
