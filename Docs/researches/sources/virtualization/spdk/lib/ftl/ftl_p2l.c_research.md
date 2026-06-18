# File Research: sources/virtualization/spdk/lib/ftl/ftl_p2l.c

Implements P2L checkpoint management for open base-device bands. Checkpoints emulate/replace VSS-style progress tracking for base writes.

Core object: `struct ftl_p2l_ckpt`, which binds a checkpoint metadata region, VSS metadata page buffer, page counts, pages-per-transfer, and debug bitmap state.

Main flows:
- `ftl_p2l_ckpt_init/deinit` allocate four checkpoint region handlers and manage free/in-use lists.
- `ftl_p2l_ckpt_issue` records an xfer-sized write request into checkpoint pages, updates band P2L entries for relocation/compaction writes, writes sequence/count/checksum metadata, and persists pages.
- Management persistence finds bands assigned to checkpoint regions and serializes their in-memory P2L into checkpoint metadata during clean shutdown.
- Restore functions recover band P2L from checkpoint pages, validate sequence IDs and CRCs, reacquire the matching checkpoint object, and place the band iterator at the restored write offset.
- Debug paths validate expected checkpoint page coverage.

Interactions: used by writers/bands to maintain crash-recoverable mapping for open bands and by management restore/finalization paths after clean or dirty startup.
