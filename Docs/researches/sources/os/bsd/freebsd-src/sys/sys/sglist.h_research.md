# File Research: sources/os/bsd/freebsd-src/sys/sys/sglist.h

Scatter/gather list API for physical address ranges.

Key responsibilities:
- Defines `struct sglist_seg` with physical address and length.
- Defines `struct sglist` with segment array, reference count, current segment count, and capacity.
- Provides inline initialization, reset, and hold/refcount helpers.
- Declares builders and appenders for kernel buffers, physical addresses, bios, mbufs, external-page mbufs, user buffers, uiomove data, and VM pages.
- Declares clone, slice, split, join, consume, count, length, and free helpers.

Important patterns:
- Segment ownership is reference-counted.
- The API can translate many FreeBSD I/O container types into a common physical-range representation.
- Slice/split helpers support passing subranges to DMA or crypto/storage consumers without rebuilding source data.

Research relevance:
- Useful substrate for block I/O, network offload, DMA programming, and zero-copy data paths.
