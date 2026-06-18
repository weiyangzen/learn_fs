# File Research: sources/local-fs/e2fsprogs/e2fsck/region.c

This file provides a small region-allocation tracker used to detect overlapping allocations within an address range.

Core data:
- `struct region_struct` stores minimum/maximum bounds, a sorted linked list of allocated extents, and a cached `last` pointer.
- `struct region_el` stores half-open `[start, end)` allocated intervals.

API:
- `region_create(min, max)` allocates and initializes an empty region.
- `region_free(region)` frees all interval nodes and the region object.
- `region_allocate(region, start, n)` attempts to reserve `[start, start+n)`.

Allocation semantics:
- Returns `0` for successful allocation.
- Returns `1` for conflict or zero-length allocation.
- Returns `-1` for out-of-range or allocation failure.
- Maintains the interval list sorted and merged.
- Fast path extends or appends after `region->last` when allocations are monotonic.
- Detects overlaps covering start, end, or entire existing intervals.
- Merges adjacent intervals on either side.

Test program:
- Under `TEST_PROGRAM`, includes a bytecode-like scripted test harness with create, allocate, print, and free operations.

Integration points:
- Included via e2fsck internals as a utility for collision detection, especially metadata/EA/extent allocation validation.

Risk notes:
- The API treats `n == 0` as a non-error conflict-like return of `1`.
- `end = start+n` assumes caller-provided values do not overflow `region_addr_t`.
