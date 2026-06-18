# File Research: sources/local-fs/erofs-utils/lib/dedupe.c

## Purpose
Rolling-hash based deduplication for uncompressed source windows during compression.

## Main Structures
- `struct z_erofs_dedupe_item`: stored dedupe candidate with rolling hash, xxhash, SHA-256 prefix, pstart/plen, original length, flags, and extra data.
- `dedupe_tree[65536]`: hash buckets.
- `dedupe_subtree`: per-file/transaction insertion chain for commit or rollback.

## Important Functions
- `erofs_memcmp2()`: optimized byte comparison returning matching prefix length.
- `z_erofs_dedupe_match()`: searches backwards over the current queue for the best matching stored window.
- `z_erofs_dedupe_insert()`: inserts an extent's original data as a future dedupe candidate.
- `z_erofs_dedupe_commit()`: either keeps or drops current transaction's inserted candidates.
- `z_erofs_dedupe_init()` / `z_erofs_dedupe_exit()`: initialize buckets/window hash constants and free state.

## Interactions
- Called from `compress.c` to replace repeated data with references to earlier compressed/raw extents.
- Uses rolling hash, xxhash, and SHA-256 to avoid expensive full comparisons unless likely matched.

## Notes
The dedupe window must be initialized nonzero; otherwise match/insert are effectively disabled.
