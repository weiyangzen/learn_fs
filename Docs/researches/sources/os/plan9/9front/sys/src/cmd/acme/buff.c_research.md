# File Research: sources/os/plan9/9front/sys/src/cmd/acme/buff.c

This file implements Acme's rune buffer abstraction backed by temporary disk blocks with a single in-memory cache.

Key responsibilities:
- `sizecache()` grows the in-memory rune cache with slop.
- `addblock()`/`delblock()` manage the buffer's array of disk `Block*` entries.
- `flush()` writes dirty cache content to disk or deletes empty blocks.
- `setcache()` locates, flushes, and loads the block containing a requested position.
- `bufinsert()` inserts runes, splitting or adding blocks as needed while respecting `Maxblock`.
- `bufdelete()` deletes ranges across cached disk blocks.
- `loadfile()` reads bytes from an fd, converts UTF to runes, handles partial UTF sequences between reads, and delegates insertion to a callback.
- `bufload()` loads into a `Buffer`.
- `bufread()` copies runes from arbitrary positions.
- `bufreset()` and `bufclose()` clear buffer storage.

Important dependencies:
- Uses `disknewblock()`, `diskwrite()`, `diskread()`, and `diskrelease()` from `disk.c`.
- Uses `cvttorunes()` for UTF conversion and `fbufalloc()`/`runemalloc()` helpers.

Filesystem/storage relevance:
- This is Acme's core text storage layer. Large files and undo/edit logs are buffered as rune blocks in a temp file rather than held fully in memory.

Notes:
- The buffer cache is write-back and position-based; edits mutate logical block layout while disk blocks are recycled through `Disk`.
- `loadfile()` is generic enough to feed both buffers and edit logs.
