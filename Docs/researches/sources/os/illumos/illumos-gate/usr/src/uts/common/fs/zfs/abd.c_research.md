# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/abd.c

## Scope

Implements ZFS ARC Buffer Data, an abstraction over linear and scattered memory buffers used by ARC, ZIO, RAID-Z, and other consumers that need block-sized data without always requiring contiguous allocation.

Read completely: 1,177 lines.

## Core Model

An `abd_t` can be:

- Linear: one contiguous `zio_buf_alloc()` or `zio_data_buf_alloc()` buffer.
- Scattered: an array of fixed-size chunks from `abd_chunk_cache`.
- Offset/view ABD: a non-owning ABD that points into another ABD and increments the parent child refcount.
- External buffer wrapper: a non-owning linear ABD created from caller-provided memory.

Scattered ABDs reduce ARC memory fragmentation by allocating page-sized chunks rather than large contiguous buffers. Small allocations default to linear buffers based on `zfs_abd_scatter_min_size`.

## Main APIs

Lifecycle and allocation:

- `abd_init()` creates the ABD chunk cache and kstats.
- `abd_fini()` tears down kstats and the chunk cache.
- `abd_alloc()` allocates scattered by default unless disabled or below threshold.
- `abd_alloc_linear()` forces contiguous storage.
- `abd_alloc_for_io()` currently uses linear ABDs for block I/O.
- `abd_alloc_sametype()` matches another ABD’s storage style and metadata flag.
- `abd_free()` frees owning ABDs.
- `abd_get_offset()` and `abd_get_offset_size()` create non-owning views.
- `abd_get_from_buf()` wraps caller-owned memory.
- `abd_put()` releases non-owning ABD structures.

Ownership conversion:

- `abd_to_buf()` returns the raw buffer for linear ABDs.
- `abd_borrow_buf()` returns a raw buffer, allocating a temporary one for scattered ABDs.
- `abd_borrow_buf_copy()` copies scattered ABD content into the borrowed buffer.
- `abd_return_buf()` returns a borrowed buffer and asserts unchanged data for scattered ABDs.
- `abd_return_buf_copy()` copies modifications back before return.
- `abd_take_ownership_of_buf()` turns a non-owning linear ABD into an owning one.
- `abd_release_ownership_of_buf()` removes ownership and clears metadata tracking.

Iteration and data operations:

- `abd_iterate_func()` maps and walks one ABD over a range.
- `abd_iterate_func2()` walks two ABDs in equal-sized mapped segments.
- `abd_copy_to_buf_off()`, `abd_copy_from_buf_off()`, `abd_copy_off()`
- `abd_cmp_buf_off()`, `abd_cmp()`
- `abd_zero_off()`

RAID-Z helpers:

- `abd_raidz_gen_iterate()` maps parity ABDs and optional data ABD segments for generation callbacks.
- `abd_raidz_rec_iterate()` maps parity ABDs and reconstruction target ABDs for reconstruction callbacks.

## State And Tunables

- `zfs_abd_scatter_enabled`: toggles scatter allocation.
- `zfs_abd_scatter_min_size`: minimum size for scatter allocation.
- `zfs_abd_chunk_size`: fixed chunk size, default 4096; iteration asserts it has not changed for existing ABDs.
- `abd_stats`: kstats for struct bytes, scatter count/data/waste, and linear count/data.
- `abd_chunk_cache`: kmem cache for scatter chunks.

## Control Flow

`abd_alloc()` computes the required chunk count, allocates an `abd_t` sized for the chunk pointer array, allocates each chunk, sets ownership, initializes child refcounting, and updates kstats. `abd_free()` requires an owning root ABD and frees either the linear buffer or all scatter chunks.

Offset ABD construction copies chunk pointers for scattered parents and preserves a per-ABD offset into the first chunk. The parent’s child refcount is incremented for the viewed byte range, and `abd_put()` decrements it.

Iteration uses `struct abd_iter`, which tracks position, mapped address, and mapped length. Linear ABDs map as one remaining span; scattered ABDs map only the current chunk suffix. All copy, compare, zero, and RAID-Z operations build on this iterator.

## Dependencies

Depends on ZFS context allocation and assertions, ZIO buffer allocators, `zfs_refcount`, kstats, `kmem_cache`, `SPA_MAXBLOCKSIZE`, RAID-Z callback contracts, and kernel preemption guards around RAID-Z mapping loops.

## Invariants And Risks

- Only owning ABDs may be freed with `abd_free()`; non-owning ABDs must use `abd_put()`.
- Parent ABDs must outlive offset ABD children.
- Metadata accounting only applies when the ABD owns the underlying buffer.
- Borrowed buffers increment child refcounts and must be returned exactly once.
- `abd_return_buf()` asserts scattered borrowed buffers are unchanged; callers intending to modify must use the `_copy` variant.
- `zfs_abd_chunk_size` is effectively boot-time only for existing scattered ABDs; runtime changes panic through iterator assertions.
- RAID-Z iteration requires progressive, 512-byte-aligned mapped lengths except at valid terminal boundaries.
