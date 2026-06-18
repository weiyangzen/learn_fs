# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_blist.c

Read completely: 1142 lines.

Implements a wired-memory bitmap block allocator using a radix tree with hints and collapsed all-free/all-allocated states. It is designed for contexts such as swap allocation where allocation and free operations must not allocate memory after initialization. The file can also be built standalone for debugging outside the kernel.

Data structures:
- `struct blist` records total managed blocks, root radix coverage, root skip distance, free block count, root metadata pointer, and number of metadata records allocated.
- `blmeta_t` is each radix-tree node. It stores either available-block count for meta nodes or a bitmap for leaves, plus `bm_bighint`, the largest-known contiguous free range hint.
- Leaf nodes cover `BLIST_BMAP_RADIX` blocks; meta nodes branch by `BLIST_META_RADIX` (16).
- The radix tree is stored in a linear array. Children immediately follow parent nodes, and `skip` values let recursion jump between child subtrees.
- A `bm_bighint` value of `(blist_blkno_t)-1` marks an out-of-range terminator for trees whose allocated metadata is smaller than the theoretical root radix.

Public API:
- `blist_create()` computes the minimal root radix/skip covering the requested block count, allocates the `struct blist`, calculates exact metadata needs by calling `blst_radix_init(NULL, ...)`, allocates metadata, initializes the tree, and returns the allocator.
- `blist_destroy()` frees the metadata array and allocator structure.
- `blist_alloc()` allocates a contiguous run and decrements `bl_free` on success; failures return `BLIST_NONE`.
- `blist_free()` frees a range and increments `bl_free`, panicking on detected inconsistencies.
- `blist_fill()` marks a range allocated regardless of current state and returns how many blocks were actually free before the fill.
- `blist_resize()` creates a new allocator, copies free-space state from the old tree, optionally frees newly added space, and destroys the old allocator.
- Under `BLIST_DEBUG`, `blist_print()` and a standalone `main()` provide interactive test commands for allocate/free/fill/resize/print.

Allocation internals:
- `blst_leaf_alloc()` handles leaf bitmaps. The one-block case uses a binary mask search; multi-block allocation scans for a contiguous set of free bits.
- `blst_meta_alloc()` handles meta nodes, respecting all-allocated and all-free collapsed states.
- When descending from an all-free meta node, `blst_meta_alloc()` lazily initializes child nodes before continuing.
- Allocation relies on `bm_bighint` to skip subtrees that cannot satisfy the request.
- On allocation failure, bighints are lowered to avoid repeating impossible searches.
- The allocator cannot allocate more than `BLIST_BMAP_RADIX` blocks per call; larger requests can panic in meta allocation.

Freeing and filling:
- `blst_leaf_free()` computes a bitmap mask for the freed range and panics if any target bit is already free.
- `blst_meta_free()` updates available counts, handles all-allocated/all-free collapsed states, recursively splits arbitrary free ranges across children, and expands bighints as children become freer.
- `blst_leaf_fill()` clears bits for a requested range and counts how many were previously free.
- `blst_meta_fill()` recursively allocates a specific range, supports all-allocated/all-free collapsed states, and decrements available counts by the number of newly filled blocks.

Copying and initialization:
- `blst_copy()` transfers free-space state from one radix tree to another by freeing corresponding ranges in the destination for every free range found in the source.
- It handles all-allocated, all-free, partial meta, and leaf bitmap cases.
- `blst_radix_init()` initializes leaves and meta nodes as all allocated, and inserts terminator nodes beyond the requested block count.
- `blst_radix_init()` is also used in sizing mode with `scan == NULL`, returning how many metadata records are required.

Standalone/debug mode:
- Outside `_KERNEL`, the file maps `kmem_alloc`, `kmem_zalloc`, and `kmem_free` to libc allocation routines, includes a local `panic()` implementation, and enables `BLIST_DEBUG` unless disabled.
- The debug CLI supports `a` allocate, `f` free, `l` fill, `r` resize, `p` print, and help commands.

Risks and notes:
- The implementation is not internally synchronized; callers must serialize access to a `blist_t`.
- `blist_create()` has comments noting unchecked arithmetic overflow while growing radix/skip.
- `blist_alloc()` does not explicitly validate `count` before reaching lower-level routines; oversized allocations can panic.
- `blist_resize()` assumes `*pbl` is a valid existing allocator and starts with the new allocator all allocated, then copies/free marks source-free regions into it.
- Hints may be too high but must never be too low; bugs in hint maintenance would cause either performance degradation or allocation failure despite available space.
