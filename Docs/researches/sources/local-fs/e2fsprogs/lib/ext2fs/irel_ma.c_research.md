# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/irel_ma.c

## Role

Memory-array implementation of the inode relocation table interface from `irel.h`.

## Main Flow

- `ext2fs_irel_memarray_create()` allocates the public vtable object, private `irel_ma`, original-inode map, relocation entry array, and per-inode reference-entry array.
- `ima_put()` stores/updates a relocation entry, preserves the original inode identity, resizes reference storage when `max_refs` changes, and updates `orig_map`.
- `ima_get()` and `ima_get_by_orig()` retrieve entries by old or original inode.
- `ima_start_iter()` / `ima_next()` iterate relocation entries.
- `ima_add_ref()` lazily allocates and appends references up to `max_refs`.
- `ima_start_iter_ref()` / `ima_next_ref()` iterate references for one inode.
- `ima_move()` moves an entry and reference list from one old inode number to another.
- `ima_delete()` clears an entry and frees its references.
- `ima_free()` releases all arrays and nested reference lists.

## Dependencies

Uses ext2fs memory allocation/resizing helpers and the `irel.h` vtable contract.

## Risks / Notes

- The source in this checkout contains malformed allocation calls around `ma->entries` and `ma->ref_entries`; as written, that section appears not to compile without macro/source correction.
- Iteration uses `while (++current < max_inode)`, so an entry exactly at `max_inode` may not be yielded.
- `ima_move()` overwrites destination entry/reference state and frees destination refs if present.
