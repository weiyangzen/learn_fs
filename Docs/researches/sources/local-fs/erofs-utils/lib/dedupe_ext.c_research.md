# File Research: sources/local-fs/erofs-utils/lib/dedupe_ext.c

## Purpose
Deduplicates already encoded extents by comparing compressed/raw output bytes against data already written to the image.

## Main Structures
- `struct z_erofs_dedupe_ext_item`: extent record plus xxhash and revoke-chain link.
- `dupl_ext[65536]`: hash buckets for encoded extents.
- `revoke_list`: transaction list for rollback.

## Important Functions
- `z_erofs_dedupe_ext_insert()`: records an encoded extent under a supplied hash.
- `z_erofs_dedupe_ext_match()`: hashes candidate bytes, reads possible matches from device, compares bytes, and returns matching physical offset or 0.
- `z_erofs_dedupe_ext_commit()`: drops transaction entries on rollback.
- `z_erofs_dedupe_ext_init()` / `z_erofs_dedupe_ext_exit()`: initialize and free state.

## Interactions
- Used by multithreaded compression merge logic in `compress.c`, especially with fragments enabled.
- Reads image data with `erofs_dev_read()` to confirm hash matches.

## Notes
`z_erofs_dedupe_ext_exit()` calls `z_erofs_dedupe_commit(true)`, which appears to target the regular dedupe transaction rather than the ext revoke list; the subsequent bucket cleanup still frees ext items.
