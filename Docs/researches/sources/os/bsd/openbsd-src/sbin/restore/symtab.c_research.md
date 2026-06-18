# File Research: sources/os/bsd/openbsd-src/sbin/restore/symtab.c

## Purpose

Maintains restore's in-memory symbol table and checkpoint file format. The table supports lookup by inode and by path, dynamic entry creation/deletion/rename, hard-link tracking, name allocation, and serialization for incremental restore resume.

## Inode And Name Lookup

The inode hash table is allocated based on `maxino / HASHFACTOR`. `lookupino()` returns the primary entry for an inode. `addino()` inserts entries by inode and checks duplicates in debug mode. `deleteino()` removes an inode's primary hash entry and clears its inode field.

`lookupname()` resolves a path by walking from `ROOTINO` through directory children. `lookupparent()` temporarily truncates the path at the final slash, looks up the parent, restores the slash, and verifies the parent is a directory. `myname()` reconstructs the current full pathname by walking parent pointers backward into a static buffer.

## Entry Lifecycle

`addentry()` uses a freelist or allocates a new `struct entry`, sets type, links it into the parent's child list, and either inserts it into the inode table or links it into an existing inode's hard-link chain for synthetic `LINK` entries. Root creation is special: it has itself as parent and must be inode `ROOTINO`.

`freeentry()` requires `REMOVED`, validates directory emptiness, removes the entry from inode or hard-link chains, removes it from the parent child list, frees its name to the string freelist, and places the entry on the entry freelist. `moveentry()` relocates an entry to a new parent/name and updates the `TMPNAME` flag based on `gentempname()`.

## Name Allocation

`savename()` and `freename()` manage variable-length names through size-class freelists indexed by allocation size increments. Freed strings are reused for later names of matching size class.

## Checkpoint Format

`dumpsymtable()` writes a symbol table snapshot unless `Nflag` is set. It assigns each entry an index, writes all names first, writes copies of entries with pointers converted to indexes/offsets, writes the inode hash table as entry indexes, and appends a `symtableheader` containing checkpoint volume, string size, table size, dump times, max inode, and tape block count.

`initsymtable(NULL)` creates a new table and root entry. `initsymtable(filename)` reads a checkpoint, validates incremental/resume tape timing, restores tape position for `R`, sets `maxino`/table size, maps the hash table into the loaded memory block, and converts indexes/offsets back into pointers.

## Risks And Invariants

- `myname()` uses a static buffer; callers must not expect stable results across subsequent calls.
- Checkpoint serialization assumes local pointer-sized placeholder fields can safely store and recover integer indexes through casts within the same architecture/build.
- `entrytblsize = maxino / HASHFACTOR` must be nonzero before creating a fresh table.
- Directory entries must be empty and unlinked before `freeentry()` accepts them.
- Path lookup mutates the input string temporarily in `lookupparent()`.
