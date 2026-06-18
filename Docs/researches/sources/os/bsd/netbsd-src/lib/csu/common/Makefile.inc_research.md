# File Research: sources/os/bsd/netbsd-src/lib/csu/common/Makefile.inc

Common CSU build rules. It sets paths and include flags, declares the startup object set, conditionally builds PIC `crtbeginS.o`, handles Alpha `crtfm.o`, and builds SPARC64 compiler memory-model note objects.

It compiles architecture `crt0.S` together with common `crt0-common.c`, links them relocatably into `crt0.o` / `gcrt0.o`, strips identifiers when requested, generates `sysident_assym.h`, and installs all startup objects into `LIBDIR`.
