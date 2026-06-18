# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/regional.c

Implements a lightweight region allocator for many short-lived allocations freed as a group.

Core behavior:
- `regional_create` creates an 8192-byte default region with the `struct regional` stored inside the first chunk.
- `regional_create_custom` allows a custom initial chunk size.
- `regional_create_nochunk` sets the large-object threshold to zero, making all user allocations separate malloc blocks.
- `regional_alloc` aligns allocations to `sizeof(uint64_t)`, serves small allocations from chunks, and puts large allocations on a separate list.
- `regional_free_all` frees secondary chunks and large allocations, then reinitializes the first chunk.
- `regional_destroy` frees all allocations and the first chunk itself.
- Helper functions copy, zero, duplicate strings, log stats, and estimate total memory.

Important details:
- Overflow protection rejects near-maximum `size_t` sizes before alignment and allocation.
- Chunk links and large-object links are stored in the first pointer-sized bytes of each allocated block.
- Large-object accounting uses `total_large`; chunk accounting is derived by walking the chunk list.
- The allocator has no per-allocation free and no cleanup callback list.

Integration points:
- Used by TCP connection limit configuration storage in this group.
- Uses `util/log.h` for assertions and stats.
