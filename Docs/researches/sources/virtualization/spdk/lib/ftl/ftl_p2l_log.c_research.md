# File Research: sources/virtualization/spdk/lib/ftl/ftl_p2l_log.c

Implements P2L IO log regions for non-VSS cache operation. Each persisted page contains a header plus multiple log items mapping LBA ranges to cache addresses and sequence IDs.

Key structures:
- `ftl_pl2_log_item`: LBA, block count, sequence ID, and FTL address.
- `ftl_p2l_log_page`: VSS/header plus packed log items, exactly one FTL block.
- `ftl_p2l_log_page_ctrl`: page plus owning log, entry index, IO list, and metadata IO context.
- `ftl_p2l_log`: per-region object with free/in-use linkage, pending IO queue, md handle, page pool, sequence ID, callbacks, and read context.

Write path: queued FTL IOs are packed into log pages, CRCed with checksum field excluded, persisted with `ftl_md_persist_entries`, and completed through the supplied callback.

Read path: pages are read concurrently through a mempool-bounded queue depth, filtered by sequence ID, validated by index/checksum/count, then expanded item-by-item through the read callback.

Notable issue: file uses `ftl_pl2_log_item` naming while the subsystem is P2L, likely a typo but functionally local.
