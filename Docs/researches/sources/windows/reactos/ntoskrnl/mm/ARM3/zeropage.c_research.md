# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/zeropage.c

## Role In Subset

Implements the ARM3 zero page thread, which converts free pages into zeroed pages for future fast allocation.

## Main Responsibilities

- Declares global `MmZeroingPageEvent`.
- Frees discardable initialization code once the zero page thread starts, via `MiFindInitializationCode` and `MiFreeInitializationCode`.
- Lowers the thread priority to zero.
- Waits on the zeroing event, removes batches of pages from the free list, maps them into reserved zeroing space, zeroes them, unmaps them, then inserts them into `MmZeroedPageListHead`.

## Important Behavior

- Batches up to `MI_ZERO_PTES` pages per zeroing pass.
- Verifies that the first global free page is also the first page removed for its page color, bugchecking with `PFN_LIST_CORRUPT` if not.
- Uses PFN lock while removing and reinserting pages, but releases it while actually zeroing memory.
- Clears the zeroing event when no free pages are available.

## Notable Limitations

- The intended idle timer wait object is commented out with a FIXME.
- The thread is an infinite kernel worker and has no explicit shutdown path.

## Filesystem-Relevant Notes

Zeroed page availability affects page-cache, mapped-file, and private-memory allocation latency because many kernel and user allocations can be satisfied from zeroed pages instead of synchronously clearing free pages.
