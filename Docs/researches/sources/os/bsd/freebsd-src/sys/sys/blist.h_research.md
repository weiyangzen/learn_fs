# File Research: sources/os/bsd/freebsd-src/sys/sys/blist.h

## Purpose
`blist.h` declares FreeBSD's bitmap resource-list allocator, historically used for swap/block allocation.

## Main Interfaces
- Defines unsigned disk address type `u_daddr_t`.
- `SWAPBLK_MASK` and `SWAPBLK_NONE` encode valid block ranges and allocation failure.
- `blmeta_t` stores bitmap and largest contiguous-block hint for a radix-tree node.
- `struct blist` tracks total blocks, available blocks, radix coverage, next-fit cursor, and root metadata.
- Functions include create/destroy, alloc/free/fill, resize, avail, print, and stats.

## Implementation Notes
Newly created lists start fully reserved; users free ranges to make them allocatable. The tree radix is the number of bits in `u_daddr_t`, and maximum single allocation is `BLIST_RADIX`.

## Dependencies and Constraints
The structure is tuned for power-of-two metadata sizes. `SWAPBLK_NONE` is an absolute sentinel value, not a flag bit, so callers must handle it distinctly from valid block numbers.
