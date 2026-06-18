# File Research: sources/os/plan9/plan9/sys/src/9/port/xalloc.c

## Role

Implements an early/kernel physical-memory-backed allocator using a fixed table of free holes. It is used for aligned low-level allocations such as descriptor tables and frame lists.

## Main Data

`Xalloc` holds a lock, a static table of 128 `Hole` records, a free-list of unused hole records, and a sorted table of available memory ranges. Allocations carry an `Xhdr` with size and `Magichole`.

## Control Flow

`xinit` divides configured memory between kernel and user page pools, limits kernel memory to `cankaddr`-addressable pages, sets `Confmem` kernel ranges, and adds kernel ranges to the hole table with `xhole`.

`xallocz` finds the first hole large enough, removes bytes from its front, writes a header, optionally zeroes, and returns user data. `xfree` validates magic and returns the whole header-sized allocation to holes. `xhole` inserts and coalesces free ranges in address order. `xspanalloc` overallocates, aligns to a requested span/alignment, and returns unused portions via `xhole`.

## Dependencies

Uses `conf`, `palloc`, `KADDR`, `PADDR`, `BY2PG`, `BY2V`, `cankaddr`, and kernel locks.

## Risks

The allocator has a fixed hole-table size; if exhausted, it logs a leak. `xspanalloc` panics on allocation failure. `xmerge` only merges adjacent allocated chunks and panics with memory dumps on bad magic.
