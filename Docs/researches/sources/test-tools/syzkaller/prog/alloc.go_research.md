# sources/test-tools/syzkaller/prog/alloc.go

## Purpose

`alloc.go` implements internal memory and virtual-memory-area allocation helpers used during syzkaller program generation.

## Important APIs, Types, And Functions

`memAlloc` tracks allocated byte ranges using a two-level bitmap, one bit per 64-byte granule. `newMemAlloc`, `noteAlloc`, `alloc`, `bankruptcy`, `pos`, `set`, and `get` manage allocation. `vmaAlloc` tracks allocated pages with `used` and `m` and provides `newVmaAlloc`, `noteAlloc`, and randomized `alloc`.

## Control Flow, State, Dependencies, And Integration

`memAlloc.alloc` normalizes zero size/alignment, scans from the last position for that alignment, marks a found range, and resets all allocations through `bankruptcy` if full before retrying. `vmaAlloc.alloc` either chooses near the end of address space or near existing used pages, records allocation, and returns the page. State is in-memory and per program-generation instance.

## Risks And Test Signals

`memAlloc` panics if total size exceeds 16 MiB or is not aligned to L0 memory. It assumes allocation requests fit; if `size > ma.size`, unsigned underflow in `end := ma.size - size` would be dangerous. `vmaAlloc.alloc` can underflow for random end placement if `size` approaches `numPages` and `r.rand(4)` is nonzero; later bounds checks panic. `alloc_test.go` covers deterministic memory allocation and randomized VMA smoke behavior.
