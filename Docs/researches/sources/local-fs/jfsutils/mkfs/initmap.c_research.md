# File Research: sources/local-fs/jfsutils/mkfs/initmap.c

Implements JFS aggregate block allocation map construction and bad-block recording for `jfs_mkfs`.

Major responsibilities:
- Builds dmap pages and dmapctl hierarchy for the block allocation map.
- Initializes the global block map control page (`dbmap`).
- Tracks allocated/free blocks through `markit`.
- Writes the completed block map to disk.
- Supports bad-block inode growth using xtree append/split logic.
- Optionally verifies unused tail filesystem blocks and records bad media blocks.

Key functions:
- `initdmap(...)`: initializes and writes one dmap page, using a reusable empty-page template for full free dmaps.
- `initctl(...)`: recursively builds dmapctl levels and child dmaps.
- `initbmap(...)`: initializes the full block map tree and writes the control page.
- `alloc_map(...)`: allocates dmap pointer array and control page.
- `initmap(...)`: initializes `dbmap` sizing, free counts, allocation group layout, and AG free counts.
- `calc_map_size(...)`: computes block-map size, initializes the block-map inode, allocates in-memory map structures, and resets allocation tracking.
- `markit(...)`: marks a block allocated or free in the working/persistent dmap maps and updates free counts.
- `write_block_map(...)`: finalizes map trees and writes the block map.
- `dbAlloc(...)`: finds contiguous free blocks for bad-block xtree page allocation.
- `xtSplitRoot(...)`, `xtSplitPage(...)`, `xtAppend(...)`: append bad-block extents to the bad-block inode xtree, splitting pages as needed.
- `verify_last_blocks(...)`: writes and reads unused blocks from `last_allocated + 1` to end of aggregate; records failed blocks into the bad-block inode.

Notable details:
- Uses endian swap helpers before on-disk writes.
- Uses `O_DIRECT` when available during verification to avoid page cache effects.
- `last_allocated` ignores bad blocks so allocator search state is based on real metadata allocations.
- `markit` checks `if (page > sz_block_map_array)`, which appears off by one; valid indices are less than `sz_block_map_array`.

Filesystem relevance: core formatter logic for on-disk JFS block allocation metadata.
