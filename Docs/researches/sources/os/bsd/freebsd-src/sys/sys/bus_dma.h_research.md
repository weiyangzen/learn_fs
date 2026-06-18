# File Research: sources/os/bsd/freebsd-src/sys/sys/bus_dma.h

## Purpose
`bus_dma.h` defines the machine-independent DMA mapping API used by FreeBSD drivers and busdma implementations.

## Main Interfaces
- DMA flags describe sleep behavior, preallocation, coherent/zeroed memory, bus-private flags, no-write/no-cache hints, page-offset preservation, and mbuf loading.
- Sync operations: preread, postread, prewrite, postwrite.
- `bus_dma_segment_t` describes DMA address/length pairs.
- Kernel APIs create/destroy DMA tags, set domains, create/destroy maps, allocate/free DMA memory, load buffers/mbufs/uio/CCBs/bios/crypto/memdesc/page arrays, sync, and unload.
- Template APIs allow stack-allocated `bus_dma_template_t`, parameter key/value filling, clone, and tag creation.
- Callback types report loaded segments and errors, with one variant including total map size.

## Implementation Notes
DMA tags encode constraints such as alignment, boundary, low/high reachable addresses, maximum transfer size, segment count, and max segment size. The newer template fill interface avoids long positional argument lists while keeping the older `bus_dma_tag_create()` ABI.

## Dependencies and Constraints
Always included through machine bus DMA headers rather than directly. Kernel-only sections depend on opaque busdma types from `sys/_bus_dma.h`, VM/page structures, and subsystem buffer descriptors.
