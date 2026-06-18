# File Research: sources/os/linux/linux/block/blk-map.c

## Summary
Maps userspace, kernel, and iterator buffers into bios attached to passthrough block requests, using direct page mapping when safe and bounce/copy buffers otherwise.

## Main Responsibilities
- Deep-copy user iovec metadata for completion-time unmap.
- Copy user data into allocated bio pages when direct mapping is unsafe.
- Pin/map user iterator pages directly when alignment and queue limits allow.
- Map kernel buffers directly or through bounce pages.
- Append mapped bios to passthrough requests while checking queue limits.
- Unmap and copy read data back to userspace after I/O completion.

## Key APIs
- `blk_rq_append_bio()`.
- `blk_rq_map_user_iov()`.
- `blk_rq_map_user()`.
- `blk_rq_map_user_io()`.
- `blk_rq_unmap_user()`.
- `blk_rq_map_kern()`.

## Important Behavior
`blk_rq_map_user_iov()` chooses copy mode for supplied `rq_map_data`, DMA alignment mismatch, non-user-backed iterators, virtual-boundary gap risk, or bvec limit mismatch. ITER_BVEC may be reused directly, but falls back to copying if request limits would require splitting.

`blk_rq_append_bio()` rejects bios that cannot fit request hardware limits without splitting, verifies merge constraints for appended bios, updates request segment counts and data length, and transfers bio crypto context ownership as needed.

For copied user reads, `bio_uncopy_user()` copies data back only if still in process context with an `mm`; orphaned workqueue completions return `-EINTR` instead of copying into an arbitrary address space.

## State and Synchronization
Request-local bio chains carry mapping state. `bio_map_data` tracks copied iterator state, whether pages are owned by the mapping code, and whether the mapping is null-mapped.

## Risks
Cleanup paths must distinguish pinned user pages, copied pages, integrity mappings, vmalloc mappings, and null-mapped data. The caller must pass the original bio chain to `blk_rq_unmap_user()` because request completion may change `rq->bio`.
