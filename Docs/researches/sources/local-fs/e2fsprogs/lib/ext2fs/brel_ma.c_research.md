# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/brel_ma.c

Implements the memory-array backend for block relocation tables. The file comments note it should be rewritten to avoid a direct array and that the module was not really used at the time.

`ext2fs_brel_memarray_create` allocates the public table, copies the name, allocates backend private state, and allocates `max_block + 1` relocation entries. It wires the table methods to local `bma_*` functions.

Backend behavior:
- `bma_put` stores an entry at index `old`.
- `bma_get` returns `ENOENT` if the entry’s `new` field is zero.
- `bma_start_iter` resets the cursor to zero.
- `bma_next` scans forward for entries with nonzero `new`; returns old block zero when exhausted.
- `bma_move` copies an entry from old to new and clears old.
- `bma_delete` clears the old entry’s `new` field.
- `bma_free` frees entries, private state, name, and table.

Implementation notes:
- Direct indexing by block number makes memory usage proportional to maximum block number.
- Some array indexes cast `blk64_t` to `unsigned`, limiting practical safety for very large values despite 64-bit parameters.
- `bma_next` uses `< ma->max_block`, so an entry exactly at `max_block` is not returned by iteration.
