# File Research: sources/os/linux/linux/block/blk-mq-dma.c

## Summary
Maps blk-mq request payloads and integrity metadata into physical vectors, DMA address iterators, and scatterlists, including support for P2PDMA and IOVA-based DMA mapping.

## Main Responsibilities
- Iterate request bio chains as mergeable physical segments.
- Map request payload segments to DMA addresses one at a time.
- Use PCI P2PDMA bus-address mappings when possible.
- Use IOVA-based DMA coalescing when segment gap and DMA merge-boundary constraints allow.
- Fall back to direct `dma_map_phys()` per segment.
- Build scatterlists for request payload and integrity metadata.

## Key APIs
- `blk_rq_dma_map_iter_start()`.
- `blk_rq_dma_map_iter_next()`.
- `__blk_rq_map_sg()`.
- `blk_rq_integrity_dma_map_iter_start()`.
- `blk_rq_integrity_dma_map_iter_next()`.
- `blk_rq_map_integrity_sg()`.

## Important Behavior
`blk_map_iter_next()` walks a request’s special payload, data bio chain, or integrity bio vectors and coalesces adjacent physical vectors when queue limits and `biovec_phys_mergeable()` allow. Segment length is capped by `get_max_segment_size()`.

DMA mapping starts by examining the first segment for P2PDMA state. Bus-address P2PDMA returns the bus address directly. Host-bridge P2PDMA uses `DMA_ATTR_MMIO` with normal DMA mapping. If IOVA mapping is suitable, the code allocates one IOVA span, links all segments, syncs it, and returns one coalesced DMA range.

Scatterlist mapping forces clearing stale sg termination bits before appending the next element, so drivers that reuse sg tables do not need to fully reinitialize them for every request.

## State and Synchronization
Mapping state is carried by caller-provided `struct dma_iova_state` and `struct blk_dma_iter`. The iterator stores current bio, bvec array, bvec iterator, integrity/data mode, P2PDMA state, DMA address, length, and status.

## Risks
The IOVA path depends on the request’s physical gap mask being compatible with the DMA device merge boundary. Error handling must destroy partially linked IOVA state. Segment counts are checked against request physical segment accounting; mismatches indicate earlier split/merge accounting bugs.
