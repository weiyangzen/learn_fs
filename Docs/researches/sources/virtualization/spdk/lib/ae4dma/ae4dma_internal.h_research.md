# File Research: sources/virtualization/spdk/lib/ae4dma/ae4dma_internal.h

`ae4dma_internal.h` defines private AE4DMA helper macros and in-memory channel/queue structures. It includes the public AE4DMA API, spec definitions, SPDK queue macros, and MMIO helpers.

It provides `upper_32_bits()` and `lower_32_bits()` helpers, descriptor-ring sizing constants, callback metadata structure `ae4dma_descriptor`, command queue structure `ae4dma_cmd_queue`, and private channel structure `spdk_ae4dma_chan`.

Each command queue tracks MMIO queue registers, DMA-visible descriptor base, callback ring, software tail, queue size, physical ring address, write index, and pending descriptor count. Each channel tracks the PCI device, max transfer size, BAR-mapped register base, fixed array of hardware queues, queue count, DMA capability flags, and global attached-list linkage.

Inline helpers report command-queue fullness and validate requested queue count against `AE4DMA_MAX_HW_QUEUES`.

Research notes: this header’s structures are used directly by `ae4dma.c`, so layout changes affect queue setup, event processing, and descriptor building.
