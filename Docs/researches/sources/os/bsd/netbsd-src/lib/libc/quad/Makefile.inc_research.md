# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/Makefile.inc

Build fragment adding quad support routines to libc. It includes comparison, division, modulo, multiplication, negation, shifts, and integer/floating conversion helpers.

The selected source set is architecture-sensitive. Generic conversion files are skipped for earm architectures, which instead use IEEE-754-specific conversion implementations plus C shift helpers. m68k/m68000 select assembly shift routines. The file also adds older bitwise/add/sub helpers with a comment noting they appear unused.

This Makefile is the build switchboard for compiler runtime-style 64-bit arithmetic support inside libc.
