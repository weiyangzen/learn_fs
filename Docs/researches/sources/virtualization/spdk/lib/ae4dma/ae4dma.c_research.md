# File Research: sources/virtualization/spdk/lib/ae4dma/ae4dma.c

`ae4dma.c` implements the AMD AE4DMA PCI DMA-engine library. It handles device enumeration, attach/detach, PCI BAR mapping, queue setup, descriptor preparation, submission doorbells, and completion polling.

The global driver state is protected by a pthread mutex and tracks attached AE4DMA channels in a TAILQ. `spdk_ae4dma_probe()` enumerates PCI devices through `spdk_pci_ae4dma_get_driver()`, skips devices already attached, runs the caller probe callback, attaches accepted devices, inserts them into the global list, and invokes the attach callback.

Attach enables PCI bus mastering, allocates a channel object, maps BAR0, configures hardware queue count, sets copy capability, initializes up to `AE4DMA_MAX_HW_QUEUES`, allocates DMA descriptor rings with `spdk_dma_zmalloc()`, translates descriptor-ring virtual addresses to physical addresses, programs queue registers, enables queues, disables interrupts, and allocates callback-ring metadata.

Copy submission is built in `spdk_ae4dma_build_copy()`. It walks source and destination iovec pairs with `spdk_ioviter`, translates each segment with `spdk_vtophys()`, splits work where physical contiguity differs between source and destination, checks descriptor-ring headroom, writes AE4DMA descriptors, and attaches the user callback only to the final descriptor in the batch.

`spdk_ae4dma_flush()` updates the hardware write index for a queue. Event processing reads descriptor status from the command queue tail, stops when it reaches a submitted descriptor, reports descriptor error codes, decrements pending descriptor count, invokes descriptor callbacks, and advances the software tail.

Detach removes the channel from the global attached list, unmaps the PCI BAR, frees each queue’s DMA descriptor memory and callback ring, and frees the channel object.

Research notes: the implementation reserves four descriptors of ring headroom before declaring a ring full. Error handling during queue startup can return after partial allocation; callers rely on destruct cleanup, so cleanup coverage for partially initialized queues is important when modifying this code.
