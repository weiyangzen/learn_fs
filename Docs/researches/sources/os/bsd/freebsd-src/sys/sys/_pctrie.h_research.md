# File Research: sources/os/bsd/freebsd-src/sys/sys/_pctrie.h

Compressed radix tree root definition.

Key elements:
- Forward-declares `struct pctrie_node`.
- Defines `struct pctrie` with a root node pointer.

Dependencies:
- None beyond standard struct declarations.

Research notes:
- Provides the shared root type for pctrie users.
- Used by `_rangeset.h`; pctries are common for sparse keyed kernel structures.
