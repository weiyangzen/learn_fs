# File Research: sources/os/bsd/freebsd-src/sbin/restore/symtab.c

Purpose: maintains restore’s in-memory symbol table and serializes/deserializes it for checkpoint and restart.

Key functions:
- `lookupino()` and `lookupname()` provide inode and pathname lookup.
- `addentry()`, `freeentry()`, `moveentry()`, `deleteino()`, and internal `removeentry()` maintain the tree, inode hash chains, and hard-link chains.
- `myname()` reconstructs a full pathname by walking parent pointers.
- `savename()` and `freename()` implement a small free-list allocator for path component strings.
- `dumpsymtable()` writes string data, pointer-indexed `entry` records, hash table indices, and a trailing `symtableheader`.
- `initsymtable()` either initializes a new root table or reads a checkpoint and converts serialized indices back into pointers.

Integration: consumed by incremental restore and interactive/extract modes. Checkpoint data includes volume number, string size, entry table size, dump times, `maxino`, and tape block count so `restore -R` can resume extraction.

Risk notes: serialization stores pointer fields as integer-like indices through casts, so format is tightly coupled to `struct entry` layout and native ABI. The string allocator assumes `NAME_MAX`-bounded component sizes. Path reconstruction uses one static buffer.
