# File Research: sources/os/bsd/freebsd-src/sbin/ipf/iplang/Makefile

This is a standalone, older-style Makefile for building the `iplang` parser objects rather than a normal FreeBSD `bsd.prog.mk` program Makefile.

Key points:
- Builds `iplang_y.o` and `iplang_l.o`, optionally under `$(DESTDIR)`.
- Generates `iplang_l.c` from `iplang_l.l` with `lex`.
- Generates `iplang_y.c` and `iplang_y.h` from `iplang_y.y` with `yacc -d`.
- Uses include paths for current directory, parent directory, destination directory, and `../ipsend`.
- `clean` removes objects and generated lex/yacc files.

This appears to support the IP packet language used by the `ipsend` family rather than installing a top-level FreeBSD program directly.
