# File Research: sources/os/bsd/freebsd-src/sys/sys/msan.h

Defines Kernel Memory Sanitizer interface hooks and no-op fallbacks.

Key content:
- Active only under `KMSAN`; otherwise every hook macro compiles to no-op.
- KMSAN state constants distinguish uninitialized and initialized shadow bytes.
- KMSAN type constants classify stack, kmem, malloc, and UMA origins.
- `KMSAN_RET_ADDR` captures caller return address.
- Declares init and shadow mapping hooks.
- Declares thread allocation/free hooks.
- Declares DMA map sync hook through `struct memdesc` and `bus_dmasync_op_t`.
- Declares origin, mark, and check functions for raw buffers, bios, mbufs, CAM CCBs, and UIOs.

Research relevance:
- Important for detecting use of uninitialized memory across storage, network, UIO, and mbuf paths.
- Interacts with `memdesc.h`, `mbuf.h`, and block I/O structures.

Cautions:
- Function names in no-op section include legacy DMA macro names as well as `kmsan_bus_dmamap_sync`.
- Requires `KMSAN` build to have any runtime effect.
