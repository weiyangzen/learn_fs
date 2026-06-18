# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_bus_dma.c

## Purpose
Provides common MI busdma helper code for locking, loading different memory descriptions into DMA maps, DMA template construction, crypto-buffer loading, and no-IOMMU fallback stubs.

## Main Elements
- `busdma_lock_mutex()`: adapts a mutex to `BUS_DMA_LOCK` / `BUS_DMA_UNLOCK`.
- `_busdma_dflt_lock()`: panic stub used when deferred DMA callbacks are impossible but a default lock is invoked.
- Internal loaders:
  - `_bus_dmamap_load_vlist()` loads virtual segment lists with offset/length clipping.
  - `_bus_dmamap_load_plist()` loads physical segment lists.
  - `_bus_dmamap_load_mbuf_epg()` handles unmapped external-page mbufs, including header, page array, and trailer.
  - `_bus_dmamap_load_single_mbuf()` and `_bus_dmamap_load_mbuf_sg()` load mbufs and chains.
  - `_bus_dmamap_load_uio()` loads user or kernel `uio` vectors using the correct pmap.
- Public load APIs:
  - `bus_dmamap_load()`, `bus_dmamap_load_mbuf()`, `bus_dmamap_load_mbuf_sg()`, `bus_dmamap_load_uio()`, `bus_dmamap_load_bio()`, `bus_dmamap_load_mem()`.
  - `bus_dmamap_load_ma_triv()` loads arrays of VM pages through physical addresses.
  - `bus_dmamap_load_crp_buffer()` and `bus_dmamap_load_crp()` load OpenCrypto buffers.
- Template helpers:
  - `bus_dma_template_init()` fills default tag constraints.
  - `bus_dma_template_fill()` applies keyed parameter overrides.
  - `bus_dma_template_tag()` creates a real DMA tag from the template.
- No-IOMMU compatibility:
  - `bus_dma_iommu_set_buswide()` returns false.
  - `bus_dma_iommu_load_ident()` returns success without doing work.

## Dependencies And Integration
Relies on machine-dependent busdma backends for `_bus_dmamap_load_buffer()`, `_bus_dmamap_load_phys()`, `_bus_dmamap_complete()`, `_bus_dmamap_waitok()`, `_bus_dmamap_load_ma()`, and optional KMSAN hooks. Integrates with mbufs, VM pages, `memdesc`, BIO, UIO, pmap, OpenCrypto, and `bus_dma_tag_create()`.

## Risk Notes
Segment counting uses the busdma convention of starting at `-1` and incrementing after load completion, which is easy to misuse. NOWAIT versus WAITOK controls callback deferral and `EINPROGRESS` behavior. Extended-page mbufs require careful offset arithmetic across headers, physical pages, and trailers. The default lock stub is intentionally fatal because deferred callbacks without a valid driver lock are a driver bug.
