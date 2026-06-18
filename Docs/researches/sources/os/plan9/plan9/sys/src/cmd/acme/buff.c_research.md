# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/buff.c

This file implements Acme’s rune buffer abstraction backed by disk blocks and a single active cache.

Key behavior:
- `bufinsert()` inserts runes, splitting or growing blocks up to `Maxblock`.
- `bufdelete()` removes ranges across cached/disk-backed blocks.
- `bufread()` reads arbitrary ranges through `setcache()`.
- `bufload()` and generic `loadfile()` convert UTF input from fd into runes, eliding NULs.
- `bufreset()` and `bufclose()` release disk blocks and cache memory.

Important details:
- Buffer data is stored in `Block`s allocated from global `disk`.
- `setcache()` flushes dirty cache before moving to the block containing a requested offset.
- `flush()` writes dirty cache or deletes an empty cached block.
- Insertions at block boundaries avoid unnecessary splits; interior insertions split the right suffix into a new block.

Filesystem relevance:
- Core text-storage layer: file contents, undo logs, edit logs, warnings, snarf buffer, and 9P data all build on this buffer.
