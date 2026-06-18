# File Research: sources/os/plan9/9front/sys/src/9/port/devswap.c

Purpose: Implements swap management and the `#¶` swap device, including the pager daemon, swap-slot accounting, encrypted swapfile access, and swap statistics/control.

Key logic:
- `swapinit` allocates the swap reference map and pageout I/O list, initializes `swapalloc`, and starts `pager`.
- Swap slots are byte-refcounted in `swmap`; `newswap`, `putswap`, `dupswap`, and `swapcount` manage slot lifetime, including overflow handling with `xref`.
- `pager` first reclaims filesystem/image/swap cache pages, then pages out eligible process segments, or kills the largest eligible process when memory cannot be recovered.
- `pageout`, `canflush`, and `pagepte` age pages, ensure TLB flushability, allocate swap slots, replace PTEs with `PG_ONSWAP`, and stage pages for I/O.
- `executeio` writes staged pages to the swap image channel and drops the extra swap/page references.
- `swap` file reports memory, page size, kernel/user/swap/reclaim, and pool statistics; writes accept `start` or an fd selecting the backing swap channel.
- `swapfile` is eve-only `ORDWR`; reads decrypt and writes encrypt one page at a time using AES-XTS before delegating to the real swap channel.

Dependencies and integration:
- Integrates with VM page tables, image/cache reclaim, process/segment locks, page allocator state, `libsec` AES-XTS, and pool memory statistics.

Risks and notes:
- The backing swap channel cannot be changed while swap is in use.
- `swapfile` requires exact page-sized I/O and allocates per-open encryption state with random keys.
- Pager locking avoids waiting on segment locks to reduce deadlock risk.
