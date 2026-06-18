# File Research: sources/os/bsd/dragonflybsd/sys/sys/bus_dma.h

Read completely: 317 lines.

This header defines the machine-independent bus DMA API.

Key contents:
- Includes machine-specific bus DMA types.
- DMA allocation/loading flags for wait behavior, coherent/zeroed memory, bounce-zone/private allocation behavior, protected calls, page-offset preservation, and uncached mappings.
- Sync operation flags for pre/post read/write.
- Opaque `bus_dma_tag_t` and `bus_dmamap_t`.
- `bus_dma_segment_t` and `bus_dmamem_t`.
- Prototypes for tag create/destroy, map create/destroy, DMA memory allocation/free, loading raw buffers, mbufs, uios, CAM CCBs, segment extraction/defrag, coherent allocation helpers, sync, and unload.
- Callback typedefs for ordinary and size-reporting DMA load completion.
- `bus_dmamap_sync` and `bus_dmamap_unload` macros skip null and `(void *)-1` maps.

Security/reliability notes:
- DMA constraints are security- and correctness-sensitive for device drivers.
- Load callbacks must correctly handle errors and segment counts before programming hardware.
- Sync flags must match device direction to avoid stale cache data or data corruption.
