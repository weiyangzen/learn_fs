# File Research: sources/os/bsd/freebsd-src/sys/sys/_bus_dma.h

Opaque bus DMA type declarations.

Defines:
- `bus_dmasync_op_t` as an integer operation type.
- Opaque pointer typedefs `bus_dma_tag_t` and `bus_dmamap_t`.
- `bus_dma_lock_op_t` enum with `BUS_DMA_LOCK` and `BUS_DMA_UNLOCK`.
- Callback type `bus_dma_lock_t(void *, bus_dma_lock_op_t)`.

Research relevance:
- Small public/kernel ABI header separating driver-visible DMA handles from machine-dependent implementation details.
