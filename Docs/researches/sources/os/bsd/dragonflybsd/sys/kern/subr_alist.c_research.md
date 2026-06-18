# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_alist.c

## Scope

This file implements `alist`, a general bitmap allocator based on a radix tree with hinting. It supports unlimited-size requests in the sense that allocations can exceed one leaf, but allocations are rounded/structured around power-of-two size and alignment constraints. The code can also be compiled stand-alone for debugging.

## Public And Internal APIs Covered

- Public allocator API: `alist_create()`, `alist_init()`, `alist_destroy()`, `alist_alloc()`, `alist_free()`, `alist_free_info()`.
- Debug API when enabled: `alist_print()` and stand-alone `main()`.
- Internal allocation/free helpers: `alst_leaf_alloc()`, `alst_meta_alloc()`, `alst_leaf_free()`, `alst_meta_free()`, `alst_radix_init()`, and debug `alst_radix_print()`.

## Control Flow And Behavior

- `alist_create()` computes the root radix and skip values needed to cover the requested block count, allocates the `struct alist` and linear radix-node array, initializes all nodes as allocated, and returns the allocator.
- `alist_init()` performs the same initialization using caller-supplied storage and asserts enough records are provided.
- `alist_alloc()` accepts any nonzero count. Non-power-of-two requests are rounded up to a power of two, allocated recursively, then the unused tail is freed.
- Power-of-two allocations search from `start` and require size-aligned results. Successful allocation decreases `bl_free`.
- `alist_free()` frees arbitrary ranges, not just power-of-two ranges, and increases `bl_free`.
- `alist_free_info()` walks toward the trailing free area and returns total free blocks plus an approximate start/count for a trailing contiguous range.
- Leaf nodes use a 32-bit bitmap where `1` means free and `0` means allocated. Single-block allocation uses a binary-search-style bit scan; larger leaf allocations scan aligned masks.
- Meta nodes use two bits per child: `00` all allocated, `01` partially free, `10` reserved/unknown, `11` all free.
- Meta allocation can allocate directly at a meta level when the requested size is at least the child radix, otherwise it descends into children whose `bm_bighint` can satisfy the request.
- Hints are conservative in the safe direction: they may be too high but are not supposed to be too low. Allocation failures reduce hints to avoid repeated futile descent.
- Freeing whole child ranges marks the child all-free at the parent. Partial frees initialize stale child state if needed, recurse, and then mark the parent entry all-free or partial based on the child's bitmap.
- `alst_radix_init()` computes memory requirements and initializes the compact linear tree without terminator nodes, relying instead on block-limit checks during allocation/free.

## State And Data Structures

- `struct alist` tracks `bl_blocks`, `bl_radix`, `bl_skip`, `bl_rootblks`, `bl_root`, and `bl_free`.
- `almeta_t` stores `bm_bitmap` and `bm_bighint`.
- Leaf radix is `ALIST_BMAP_RADIX`; meta radix is `ALIST_META_RADIX`.
- Stand-alone mode maps kernel allocation/assert/print primitives to libc equivalents.

## Dependencies

- Kernel builds include VM and malloc headers plus `sys/alist.h`; userland debug builds include standard C headers and local compatibility macros.
- The allocator is suitable for resource maps where allocation units are abstract blocks and all metadata must be preallocated.

## Risks And Invariants

- Allocation results are power-of-two aligned to the allocation size.
- Freeing an already-free leaf bit panics.
- Callers must not free outside `bl_blocks`.
- `bm_bighint` correctness is performance-critical and can affect address-specific allocation success; frees deliberately overstate hints when exact recomputation would be expensive.
- Non-power-of-two allocation works by overallocating and freeing the tail, so the free path must correctly handle arbitrary ranges.
