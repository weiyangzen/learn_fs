# File Research: sources/teaching/xv6-public/kalloc.c

Implements the physical page allocator.

Key behavior:
- Maintains a singly linked free list of 4096-byte pages.
- Initializes in two phases: `kinit1` without locking for early mapped memory, then `kinit2` enabling locks after full kernel page tables and AP startup.
- `freerange` rounds up the start address and frees each page.
- `kfree` validates alignment/range, fills freed memory with junk, and pushes it onto the free list.
- `kalloc` pops one page or returns null.

Important interactions:
- Provides memory for user pages, kernel stacks, page tables, and pipe buffers.
- Validation rejects frees below kernel `end` or at/above `PHYSTOP`.
