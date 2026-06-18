# File Research: sources/os/bsd/netbsd-src/lib/libarch/sparc/Makefile.inc

Build fragment for SPARC libarch subdirectories.

Key behavior:
- Adds `sparc/v8` as a subdirectory only when `${MACHINE_ARCH} == "sparc"`.

Dependencies:
- NetBSD make machine-architecture selection.
