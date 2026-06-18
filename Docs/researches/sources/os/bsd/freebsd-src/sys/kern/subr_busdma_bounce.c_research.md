# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_busdma_bounce.c

## Purpose
Common busdma bounce-page management code included by busdma backends that need low-address/alignment-safe DMA buffers.

## Main Elements
- `struct bounce_page`: tracks bounce KVA, bus address, original data address/page/offset/count, and queue linkage.
- `struct bounce_zone`: groups bounce pages by low-address, alignment, optional NUMA domain, counters, waiting maps, and sysctl tree.
- Global state:
  - `bounce_lock`, total page counters, zone list, deferred callback list, and `hw.busdma.total_bpages`.
- Reservation and allocation:
  - `_bus_dmamap_reserve_pages()` reserves pages or queues WAITOK maps for deferred retry.
  - `alloc_bounce_zone()` reuses or creates a suitable zone, exports per-zone sysctls, and starts the `busdma` kernel thread.
  - `alloc_bounce_pages()` allocates contiguous bounce pages under the zone's low-address and alignment constraints.
  - `reserve_bounce_pages()` updates free/reserved counts and per-map reservations.
- Address and segment helpers:
  - `addr_needs_bounce()` tests lowaddr/highaddr exclusion and alignment.
  - `add_bounce_page()` consumes a reserved page, records original data mapping, optionally preserves page offset, and returns the bounce bus address.
  - `_bus_dmamap_addseg()` and `_bus_dmamap_addsegs()` coalesce or split DMA segments under boundary, max segment, and segment-count constraints.
- Cleanup and deferral:
  - `free_bounce_pages()` returns active pages, wakes queued maps whose reservations can now be satisfied, and schedules callbacks.
  - `busdma_thread()` runs deferred loads under the driver's DMA lock and accounts deferred time.

## Dependencies And Integration
This file is designed to be included into architecture-specific busdma implementations, not compiled alone. It assumes `M_BUSDMA`, `struct bus_dmamap`, `hw_busdma`, DMA-tag field macros, optional domain macros, and backend load/sync code are already available.

## Risk Notes
Bounce accounting must keep `free_bpages`, `reserved_bpages`, `active_bpages`, and per-map `pagesneeded/pagesreserved` consistent under `bounce_lock`. WAITOK deferral re-enters `bus_dmamap_load_mem()` from a kernel thread while holding the driver lock, so incorrect lock callbacks can deadlock. `BUS_DMA_KEEP_PG_OFFSET` mutates bounce page virtual/bus addresses temporarily and must reset them on free.
