# File Research: sources/os/bsd/dragonflybsd/sys/sys/alist.h

Read completely: 110 lines.

This header defines the API and metadata for an aligned power-of-two resource bitmap allocator.

Key contents:
- Describes a radix tree with radix-16 meta nodes and radix-32 leaves.
- `alist_bmap_t` and `alist_blk_t` are 32-bit.
- `almeta_t` stores a bitmap and biggest contiguous allocation hint.
- `alist_t` tracks total blocks, radix, skip, free count, root pointer, and root coverage.
- Constants for meta/leaf radix, no-block sentinel, and known record counts.
- Prototypes for create/init/destroy, alloc/free, free-info query, and print.

Security/reliability notes:
- No implementation here. Allocation correctness depends on the implementation maintaining biggest-hint values that are never too small.
- Non-power-of-two allocations are rounded internally by the allocator, so callers must account for alignment behavior.
