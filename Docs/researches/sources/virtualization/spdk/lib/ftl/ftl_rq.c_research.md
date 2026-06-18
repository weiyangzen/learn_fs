# File Research: sources/virtualization/spdk/lib/ftl/ftl_rq.c

Defines allocation, destruction, and unpinning for internal FTL transfer requests.

`ftl_rq_new` allocates a request sized for `dev->xfer_size` entries, DMA payload buffer, optional DMA metadata buffer, and initializes each entry with index, invalid address/LBA, payload pointer, optional metadata pointer, and zero sequence ID.

`ftl_rq_del` frees DMA payload, DMA metadata, and the request object.

`ftl_rq_unpin` walks entries up to `rq->iter.count` and calls `ftl_l2p_unpin` for any pin context whose LBA is valid.

This utility underpins relocation, NV-cache compaction, writer padding, and checkpoint IO paths.
