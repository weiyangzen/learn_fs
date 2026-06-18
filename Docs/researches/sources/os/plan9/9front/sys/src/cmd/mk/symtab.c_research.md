# File Research: sources/os/plan9/9front/sys/src/cmd/mk/symtab.c

Implements mk’s multi-namespace hash table.

Key behavior:
- Uses a fixed 4099-bucket hash table and `HASHMUL` rolling hash seeded by symbol space.
- `symlook()` finds or optionally installs a symbol in a given namespace.
- `symtraverse()` calls a function for each symbol in a namespace.

Important dependencies: `mk.h`, `Malloc`.

Notable risks:
- Symbol storage is process-lifetime; there is no deletion path.
- Different logical namespaces share the same hash table but are separated by `space`.
