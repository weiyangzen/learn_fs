# File Research: sources/os/plan9/9front/sys/src/cmd/aux/8prefix.c

Object-file rewriting tool for Plan 9 386 `.8` files. It prefixes externally visible symbols inside object files and optionally renames `main`.

Important behavior:
- Reads each object file completely into memory, parses 8c object records using `/sys/src/cmd/8c/8.out.h`.
- Maintains a hash table of `Sym` records; static symbols are versioned per object file so identical static names remain separate.
- `walkobj()` parses `ANAME`/`ASIGNAME` and instruction records, using `zaddr()` to advance encoded addresses and resolve symbol references.
- `renamesyms()` assigns `prefix + oldname` to version 0 symbols used by global/data/text records, except `main` when `-m` is supplied.
- Rewrites object files in place, substituting symbol names on `ANAME`/`ASIGNAME`.

Filesystem relevance:
- In-place mutation of object files; useful for namespace isolation when linking generated or embedded code.
