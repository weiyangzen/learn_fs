# File Research: sources/os/bsd/netbsd-src/sys/sys/blist.h

## Scope

Declares the bitmap resource list allocator interface.

## APIs And Data Structures

- Defines `blist_bitmap_t` and `blist_blkno_t` as `uint32_t`.
- Uses opaque `blist_t`.
- `BLIST_NONE` signals allocation failure.
- `BLIST_BMAP_RADIX` is bits per bitmap word; `BLIST_MAX_ALLOC` equals one radix.
- Declares `blist_create`, `blist_destroy`, `blist_alloc`, `blist_free`, `blist_fill`, `blist_print`, and `blist_resize`.

## Behavior

- New blists start fully reserved; callers free ranges before general allocation.
- Intended for block-like resource allocation, with practical limits far below the theoretical 2^31 block capacity.

## Risks And Invariants

- `BLIST_NONE` is an absolute sentinel, not a flag bit.
- Allocation unit and maximum allocation are tied to `blist_bitmap_t` width.
