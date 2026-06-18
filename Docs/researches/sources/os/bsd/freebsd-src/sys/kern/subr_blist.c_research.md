# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_blist.c

## Summary
Implements a wired-memory radix-tree bitmap allocator used for block ranges such as swap space. It tracks free blocks with leaf bitmaps and meta-node hints so allocations and frees do not need to allocate memory or block on the VM system.

## Main Responsibilities
- Creates and destroys block-list allocator instances sized for a fixed number of blocks.
- Allocates a contiguous block range with minimum and maximum requested sizes.
- Frees arbitrary block ranges.
- Fills/reserves arbitrary ranges regardless of prior allocation state.
- Resizes an existing allocator by creating a new tree and copying free ranges.
- Reports free-block availability and fragmentation statistics.
- Includes optional standalone debug printing and an interactive test harness.

## Key APIs
- `blist_create()`, `blist_destroy()`.
- `blist_alloc()`, `blist_free()`, `blist_fill()`, `blist_resize()`.
- `blist_avail()`, `blist_stats()`.
- Debug-only `blist_print()` and standalone `main()`.

## Important Behavior
The radix tree is stored in a compact linear array. Each leaf bitmap bit represents one free block. Each meta-node bitmap bit means the corresponding subtree contains at least one free block. Each node also has `bm_bighint`, an upper-bound hint for the largest allocation that may start in that subtree.

`blist_create()` computes the minimum number of nodes needed for the requested block count and may add a sentinel node when the block count is exactly leaf-aligned so cross-leaf scans stay inside the allocation.

`blist_alloc()` starts at `bl_cursor`, falls back to zero on failure, updates `bl_avail`, and advances/wraps the cursor on success. The minimum requested count must not exceed `BLIST_MAX_ALLOC`; allocation can return up to `maxcount` blocks.

Leaf allocation uses bit tricks to find a run of set bits at least as large as the requested count. If a run reaches a leaf boundary, `blst_next_leaf_alloc()` can consume leading free bits in following leaves and clears parent bits for subtrees that become fully allocated.

Freeing recursively sets leaf/meta bitmap bits and pessimistically resets `bm_bighint` to `BLIST_MAX_ALLOC`. Filling recursively clears bits and returns how many blocks were newly allocated by the fill.

`blist_stats()` scans the tree while skipping fully allocated subtrees, computes maximal free-range statistics, and buckets gap sizes using Fibonacci ranges.

## Dependencies
Kernel builds use `M_SWAP`, malloc/free, sbuf, bit counting, and kernel assertions. Standalone debug builds provide libc substitutes and include an interactive test loop.

## Risks
The allocator is not internally locked; callers must serialize access. Allocation cannot satisfy minimum requests larger than `BLIST_MAX_ALLOC`, though freeing/filling can operate on arbitrary ranges. Hints are upper bounds and can be loose after frees, so allocation correctness does not require tight hints but performance depends on maintaining them well enough.
