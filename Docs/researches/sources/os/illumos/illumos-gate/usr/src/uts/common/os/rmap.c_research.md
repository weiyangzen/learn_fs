# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/rmap.c

## Purpose

Compatibility wrapper implementing legacy resource-map allocation interfaces on top of the kernel `vmem` allocator.

## Key Interfaces

- `rmallocmap()` and `rmallocmap_wait()` create a `vmem` arena named `rmap` with non-sleeping or sleeping allocation behavior.
- `rmfreemap()` destroys the arena.
- `rmalloc()` and `rmalloc_wait()` allocate from the arena and return the address as `ulong_t`.
- `rmfree()` frees an existing contained range, or adds the range to the arena if it was not already contained.

## Dependencies

Uses `vmem_create()`, `vmem_destroy()`, `vmem_alloc()`, `vmem_contains()`, `vmem_free()`, `vmem_add()`, and `cmn_err()`.

## Notes for Future Work

- `rmfree()` warns if it cannot add an out-of-arena segment back to the vmem arena.
- The legacy `mapsize` parameter is ignored because `vmem` supplies the backing behavior.
