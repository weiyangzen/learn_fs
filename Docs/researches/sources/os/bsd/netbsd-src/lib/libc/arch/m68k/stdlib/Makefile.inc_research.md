# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/stdlib/Makefile.inc

This make include adds m68k assembly implementations of `abs.S` and `llabs.S` to libc’s stdlib build. It is a source-selection file only.

The integration risk is build coverage: removing these entries would fall back to generic code or leave expected m68k symbols unbuilt.
