# File Research: sources/os/bsd/openbsd-src/sys/kern/subr_blist.c

## Role

Implements a preallocated bitmap allocator using a hinted radix tree. It is used for block-like allocation where allocation and free paths must avoid recursive memory allocation, notably swap-space style management.

## Key Behavior

- `blist_create()` computes the radix/skip layout, allocates the `struct blist` and fixed root array, and initializes the radix tree as all allocated.
- `blist_alloc()` and `blist_allocat()` reserve contiguous blocks, decrementing `bl_free` on success.
- `blist_free()` releases a range and panics on inconsistent double-free conditions.
- `blist_fill()` marks a region allocated regardless of prior state and returns how many blocks were newly consumed.
- `blist_resize()` creates a new tree, copies free regions from the old tree, optionally frees newly added blocks, and destroys the old tree.
- `blist_gapfind()` scans for the largest fully free leaf-aligned gap.
- Leaf helpers operate on bitmaps, optimizing single-block allocation and full-bitmap states.
- Meta helpers manage collapsed all-free/all-allocated states, recursively initialize stale children when needed, and maintain `bm_bighint`.
- Debug/standalone code can print and interactively test the allocator outside the kernel.

## Interfaces And Dependencies

Uses `swblk_t`, `blmeta_t`, `blist_t`, `SWAPBLK_NONE`, `BLIST_BMAP_RADIX`, and `BLIST_META_RADIX` from `sys/blist.h`. Kernel builds allocate from `M_VMSWAP`; non-kernel builds provide testing shims.

## Notes

Hints are conservative: they may be too high until failed searches refine them, but should not be too low. Allocation is limited to at most one leaf radix per call, while free/fill can span arbitrary ranges.
