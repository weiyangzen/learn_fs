# File Research: sources/os/bsd/netbsd-src/sys/sys/bus_proto.h

## Scope

Declares machine-independent bus_space(9) and bus_dma(9) function prototypes and flags.

## APIs And Behavior

- Defines bus space map flags: cacheable, linear, prefetchable.
- Defines bus space barrier flags for read and write ordering.
- Declares bus space map/unmap/subregion/alloc/free/mmap/vaddr/barrier.
- Declares scalar read/write accessors for 1/2/4 bytes and optional 8-byte accessors, including stream variants.
- Declares multi and region read/write prototypes via macros, with KASAN/KCSAN/KMSAN wrapper redirection when enabled.
- Declares set/copy multi/region operations for normal and stream access.
- Declares bus space equality helpers.
- Defines bus DMA flags for sleep behavior, allocation timing, coherent/streaming/cache hints, bus-private flags, read/write direction, and sync operation flags.
- Declares DMA map create/destroy/load/unload/sync, DMA memory alloc/free/map/unmap/mmap, DMA tag subregion, and tag destroy.

## Dependencies

- Uses bus types from machine definitions and optional sanitizer config headers.

## Risks And Invariants

- Sanitizer wrapper macros must match every memory accessor width and variant.
- Direction and sync flags encode cache-coherency protocol; misuse can corrupt DMA transfers.
