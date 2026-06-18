# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_sglist.c

## Purpose

`subr_sglist.c` implements scatter/gather list construction and manipulation. It converts kernel buffers, user buffers, bios, mbufs, VM page arrays, uios, physical address ranges, and existing sglist ranges into arrays of contiguous physical segments.

## Main Data Model

An `sglist` owns:

- `sg_nseg`: current number of segments.
- `sg_maxseg`: capacity.
- `sg_refs`: reference count.
- `sg_segs[]`: array of `struct sglist_seg`, each with physical address and length.

A local `struct sgsave` records `sg_nseg` and the old length of the final segment. The `SGLIST_SAVE`/`SGLIST_RESTORE` macros roll back failed append attempts because appends only grow the list or extend the last segment.

## Segment Appending

`_sglist_append_range()` appends a physical range, coalescing with the previous segment when `previous_paddr + previous_len == paddr`. It returns `EFBIG` if capacity is exhausted.

`_sglist_append_buf()` maps a virtual buffer through either kernel pmap extraction or a supplied user pmap, splits by page boundaries, and appends physical runs. It optionally reports how much was appended before a capacity failure.

`sglist_append()`, `sglist_append_user()`, `sglist_append_phys()`, `sglist_append_vmpages()`, `sglist_append_sglist()`, `sglist_append_uio()`, `sglist_append_bio()`, `sglist_append_mbuf()`, `sglist_append_single_mbuf()`, and `sglist_append_mbuf_epg()` are type-specific wrappers. Most save and restore state so failures do not leave partial additions.

`sglist_consume_uio()` is intentionally different: it appends as much as fits, advances the `uio` by the completed amount, and returns success even when it stops due to list capacity.

## Counting And Allocation

`sglist_count()` counts physical runs needed for a kernel virtual buffer.

`sglist_count_vmpages()` counts runs in an array of VM pages.

`sglist_count_mbuf_epg()` counts runs for an `M_EXTPG` mbuf, including header, page array, and trailer.

`sglist_alloc(nsegs, mflags)` allocates a list plus segment storage in one block and initializes it. `sglist_free()` drops a reference and frees on last reference. `sglist_build()` counts, allocates, and populates a list for one kernel buffer. `sglist_clone()` duplicates list metadata and active segments.

`sglist_length()` sums segment lengths.

## List Transformations

`sglist_split(original, head, length, mflags)` moves the first `length` bytes from `original` into `*head`. It rejects shared originals (`sg_refs > 1`) with `EDOOFUS`. It may allocate `*head`, validates capacity/emptiness for caller-provided heads, handles splitting inside a segment, and removes copied segments from the front of the original.

`sglist_join(first, second)` appends all segments from `second` into `first`, coalescing the boundary if adjacent and resetting `second`.

`sglist_slice(original, slice, offset, length, mflags)` copies a logical byte range from `original` into `*slice`, adjusting first and last segments for partial overlap.

## Dependencies

The file depends on VM/pmap extraction, mbuf extended-page layout, `bio` unmapped-buffer conventions, `uio`, malloc, refcounting, and KTR tracing.

## Maintenance Notes

Rollback behavior is central: append wrappers generally leave the destination unchanged on `EFBIG` or `EINVAL`. New append paths should use the existing save/restore pattern unless partial consumption is explicitly desired.

The direct segment-array transformations in split/join/slice are higher-risk than the append wrappers. They must preserve copy direction, segment counts, and in-place overlap behavior, especially when trimming the front of `original` or moving segments between lists.
