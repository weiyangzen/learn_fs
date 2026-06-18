# File Research: sources/os/plan9/plan9/sys/src/9/port/swap.c

Implements swap-slot allocation and the pager daemon.

Swap allocation:
- `swapinit` allocates the swap reference map and page I/O list; initializes `swapimage.notext`.
- `newswap` finds a free swap slot, marks it referenced, and returns disk address.
- `putswap`, `dupswap`, and `swapcount` maintain per-slot reference counts.
- `setswapchan` installs the swap channel, optionally shrinking configured swap to file/partition size.
- `swapfull` reports when free swap falls below 10%.

Pager:
- `kickpager` starts or wakes the `pager` kproc.
- `pager` sleeps until memory pressure, then scans processes/segments, pages out eligible pages, or kills a large process if no swap channel exists.
- `needpages` compares `palloc.freecount` with `swapalloc.headroom`.
- `canflush` verifies all processes sharing a segment can flush TLBs before paging.
- `pageout` scans PTEs, uses reference-generation aging, and calls `pagepte`.
- `pagepte` drops text pages back to demand-load or assigns swap addresses for data/BSS/stack/shared pages, caching pages under `swapimage` while I/O is pending.
- `executeio` sorts pages by swap address and writes them to the swap channel in batches.
- `pagersummary` reports memory/swap/iolist counts.

Important behavior:
- Text pages are discarded rather than written to swap.
- Dirty anonymous/shared pages are written to swap and represented in PTEs as `daddr|PG_ONSWAP`.
- A page is temporarily refcounted while being written to prevent reuse.
- Page aging uses `genclock`, `genage`, and `PG_REF` clearing.

Role:
- Memory-pressure backstop for the Plan 9 VM system.
