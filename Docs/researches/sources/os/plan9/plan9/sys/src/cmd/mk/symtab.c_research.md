# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/symtab.c

Implements `mk`’s hash-based symbol table.

Key functions:
- `syminit()` clears all hash buckets.
- `symlook(sym, space, install)` finds or optionally installs a symbol in a namespace.
- `symdel(sym, space)` removes matching symbols.
- `symtraverse(space, fn)` applies a callback to symbols in one namespace.
- `symstat()` prints bucket length distribution.

Behavior notes:
- Hash combines namespace and string bytes with multiplier `79`.
- Symbols are separated by `space`, allowing same name in different logical tables.
- Comments acknowledge memory leaks in deletion paths.
