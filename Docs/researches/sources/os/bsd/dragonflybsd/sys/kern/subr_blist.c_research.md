# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_blist.c

## Scope

This file implements `blist`, DragonFlyBSD's radix-tree bitmap allocator/deallocator used for block resources such as swap. It wires all metadata at creation time, supports fast allocation/free under fragmentation, supports allocation at or after a target block, filling ranges, resizing, and stand-alone debug mode.

## Public And Internal APIs Covered

- Public allocator API: `blist_create()`, `blist_destroy()`, `blist_alloc()`, `blist_allocat()`, `blist_free()`, `blist_fill()`, `blist_resize()`.
- Debug API when enabled: `blist_print()` and stand-alone `main()`.
- Internal helpers: `blst_leaf_alloc()`, `blst_meta_alloc()`, `blst_leaf_free()`, `blst_meta_free()`, `blst_leaf_fill()`, `blst_meta_fill()`, `blst_copy()`, `blst_radix_init()`, and debug `blst_radix_print()`.

## Control Flow And Behavior

- `blist_create()` computes a root radix large enough to cover the requested block count, computes skip values for the linearized tree layout, allocates the root node array, and initializes all blocks allocated.
- `blist_alloc()` allocates the first range of `count` contiguous free blocks. `blist_allocat()` does the same but only considers ranges at or beyond `blkat`.
- `blist_free()` frees an arbitrary range and panics if consistency checks detect freeing already-free blocks.
- `blist_fill()` marks a range allocated regardless of prior state and returns how many blocks were actually free before the fill.
- `blist_resize()` creates a new allocator, copies free extents from the old tree into the new one, optionally frees newly added space, swaps the pointer, and destroys the old tree.
- Leaf nodes store one bit per block; `1` means free. Single-block allocation uses a fast bit search; multi-block allocation scans contiguous masks.
- Meta nodes store available-block counts in `bmu_avail` and largest-free hints in `bm_bighint`.
- Meta nodes collapse two states: all allocated (`bmu_avail == 0`) and all free (`bmu_avail == radix`). In collapsed states, lower-level node data is considered stale and reinitialized only when descent is required.
- Allocation descends only into children whose hint can satisfy the request and whose range is beyond `blkat`. Failures lower hints to avoid repeated futile searches.
- Freeing an all-allocated meta node initializes child state unless the free covers the whole node, then recursively frees the affected range and raises hints from child hints.
- Filling can short-circuit whole-node allocation and otherwise descends to count and clear free bits.
- `blst_copy()` reconstructs free space in a destination allocator by walking free state in a source tree.

## State And Data Structures

- `struct blist` tracks `bl_blocks`, `bl_radix`, `bl_skip`, `bl_rootblks`, `bl_root`, and `bl_free`.
- `blmeta_t` uses `bm_bighint` and a union for either leaf bitmap (`bmu_bitmap`) or meta available count (`bmu_avail`).
- Terminator nodes are represented by `bm_bighint == (swblk_t)-1` when the linear tree allocation stops before the nominal root radix.
- Kernel builds allocate metadata from `M_SWAP`.

## Dependencies

- Kernel builds depend on `sys/blist.h`, kernel malloc, and panic/assert helpers.
- The allocator is designed for consumers such as swap where allocation/free paths should not allocate additional memory.

## Risks And Invariants

- Allocation larger than a child radix can panic in recursive paths; comments note the allocator historically cannot allocate more than `BLIST_BMAP_RADIX` blocks per call in some cases.
- `bm_bighint` must never be too low; stale high hints are tolerated but cost extra descent.
- Collapsed meta states intentionally invalidate lower tree contents; code must reinitialize before descending.
- Resizing preserves free extents by copying source state into a fresh all-allocated destination.
- Free and fill ranges must remain inside the allocator's represented block count.
