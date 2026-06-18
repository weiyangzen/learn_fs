# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_extent.c

Read completely: 1188 lines.

Implements NetBSD's general-purpose extent manager for tracking allocated address/resource ranges. It supports dynamically allocated extents and fixed-storage extents for early boot or constrained callers, with a global `extent_region` pool and optional preallocated region descriptors.

Core behavior:
- `extent_create()` builds an extent over `[start, end]`, optionally using caller-provided fixed storage and prepopulating a descriptor freelist.
- `extent_alloc_region()` allocates an exact range, detects conflicts in the sorted allocated-region list, and can wait on the extent CV with `EX_WAITSPACE`/`EX_CATCH`.
- `extent_alloc_subregion1()` implements first-fit or best-fit allocation inside a subrange with alignment, skew, boundary, and `EX_BOUNDZERO` handling.
- `extent_insert_and_optimize()` inserts allocated ranges and coalesces adjacent regions unless `EXF_NOCOALESCE` is set.
- `extent_free()` removes, trims, or splits an allocated region and wakes waiters.
- `extent_destroy()` and `extent_print()` free/debug the tracked map.

Concurrency and risks:
- Normal extents use `ex_lock` and `ex_cv`; `EX_EARLY` extents intentionally skip locking.
- Descriptor allocation must happen before taking the extent lock because it may sleep.
- Fixed extents can block waiting for descriptors unless `EX_MALLOCOK` or non-wait flags change behavior.
- Freeing partial regions is disallowed under `EXF_NOCOALESCE`; only exact descriptor removal works.
- The allocator has many overflow-sensitive checks around `start + size`, alignment, and boundary calculations.
