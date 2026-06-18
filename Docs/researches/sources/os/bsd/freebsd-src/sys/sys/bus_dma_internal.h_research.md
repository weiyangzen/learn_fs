# File Research: sources/os/bsd/freebsd-src/sys/sys/bus_dma_internal.h

## Purpose
`bus_dma_internal.h` declares the internal contract between machine-dependent and machine-independent busdma layers.

## Main Interfaces
- `_bus_dmamap_complete()` finalizes segment loading.
- `_bus_dmamap_load_buffer()` loads virtual buffers with a pmap.
- `_bus_dmamap_load_ma()` loads VM page arrays.
- `_bus_dmamap_load_phys()` loads physical ranges.
- `_bus_dmamap_waitok()` handles deferred waitable loads and callback state.

## Implementation Notes
This is explicitly not driver-facing. It provides the hooks MI code can call into MD implementations for the actual address translation and segment construction work.

## Dependencies and Constraints
Assumes busdma types, `struct pmap`, `struct vm_page`, `struct memdesc`, and DMA callback types are already in scope through the including busdma implementation.
