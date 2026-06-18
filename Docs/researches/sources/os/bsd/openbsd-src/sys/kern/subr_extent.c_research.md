# File Research: sources/os/bsd/openbsd-src/sys/kern/subr_extent.c

## Role

Implements a general-purpose extent manager for reserving and freeing address/resource ranges. It tracks allocated regions in a sorted list, supports fixed-storage operation for constrained contexts, and provides aligned/bounded allocation.

## Key Behavior

- `extent_create()` creates either a dynamically allocated extent or a fixed-storage extent with preallocated region descriptors; `EX_FILLED` can mark the full range allocated initially.
- `extent_destroy()` frees all region descriptors and the extent descriptor when dynamic.
- `extent_insert_and_optimize()` inserts allocated regions into sorted order and coalesces adjacent regions unless `EX_NOCOALESCE` is set.
- `extent_alloc_region()` and `extent_alloc_region_with_descr()` reserve a specific range, optionally waiting for space or tolerating conflicts.
- `extent_do_alloc()` implements subregion allocation with power-of-two alignment, skew, boundary crossing limits, first-fit (`EX_FAST`) or best-fit behavior, and optional waiting.
- `extent_alloc_subregion()` and descriptor variants wrap `extent_do_alloc()`.
- `extent_free()` removes or shrinks allocated regions, handles middle splits, supports partial conflict-tolerant frees, and wakes waiters.
- Region descriptor helpers allocate from a pool for dynamic extents or from a fixed freelist, with optional fallback to mallocable descriptors.
- Diagnostic/DDB support registers extents globally and prints all tracked regions.

## Interfaces And Dependencies

Uses `struct extent`, `struct extent_region`, `struct extent_fixed`, flags such as `EX_WAITOK`, `EX_WAITSPACE`, `EX_FAST`, `EX_NOCOALESCE`, `EX_BOUNDZERO`, and pool allocation for dynamic descriptors.

## Notes

This allocator models allocated regions, not free regions. Its correctness relies on sorted non-overlapping region lists, careful overflow checks, and descriptor availability before operations that may split or coalesce ranges.
