# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_busdma.c

Small bus-DMA convenience layer for coherent memory allocation and mbuf DMA loading with defragmentation fallback.

Key responsibilities:
- `bus_dmamem_coherent()` creates a DMA tag, allocates coherent memory, loads the DMA map, and returns virtual address, tag, map, and bus address through `bus_dmamem_t`.
- `_bus_dmamem_coherent_cb()` records the single DMA segment bus address and asserts that exactly one segment is returned.
- `bus_dmamem_coherent_any()` wraps coherent allocation for unrestricted address ranges and returns the virtual address plus raw tag/map/busaddr outputs.
- `bus_dmamap_load_mbuf_defrag()` retries mbuf segment loading after `m_defrag()` when the first load fails with `EFBIG`.

Important behavior:
- Coherent allocation constrains the tag to one segment of `maxsize`.
- If `bus_dmamap_load()` reports `EINPROGRESS` for coherent memory, the helper panics instead of supporting asynchronous completion.
- On allocation or map-load failure, the helper unwinds the tag/map/allocation and clears the caller's `bus_dmamem_t`.

Dependencies:
- Depends on bus_dma tag/map APIs, mbufs, `m_defrag()`, and `BUS_DMA_COHERENT`.

Notable risks:
- Callers receiving pointers from `bus_dmamem_coherent_any()` must retain and free the returned tag/map using the expected bus-DMA APIs.
- The mbuf defrag helper uses `M_NOWAIT`, so high pressure can surface as `ENOBUFS`.
