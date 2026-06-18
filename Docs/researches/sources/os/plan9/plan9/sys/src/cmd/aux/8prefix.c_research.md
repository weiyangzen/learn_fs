# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/8prefix.c

Object-file rewriting tool for Plan 9 8c `.8` files. It pre-resolves and prefixes external/global symbol names so linked objects cannot access them directly; it can optionally leave `main` unchanged with `-m`.

It parses 8.out object records, builds a symbol table keyed by name/version, marks global symbols found in `AGLOBL`, `AINIT`, `ADATA`, and `ATEXT`, rewrites `ANAME`/`ASIGNAME` records with prefixed names, and writes back in place.

This is architecture-specific to 386/8c object format and depends on `/sys/src/cmd/8c/8.out.h`.
