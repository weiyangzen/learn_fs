# File Research: sources/os/bsd/netbsd-src/sys/fs/udf/udf_strat_sequential.c

Read completely: 737 lines.

Implements the sequential-media UDF strategy for recordable optical media, with separate queues for reading, fixed writes, and sequential writes. It owns a descriptor pool, a scheduler thread, condition variable/mutex, queue state, a sync request flag, and saved device disk-strategy settings.

Descriptor operations are similar to the direct strategy for allocation and reads, but writes account for VAT-style virtual partitions. `udf_write_logvol_dscr_seq()` writes descriptors at translated fixed positions for non-VAT partitions, while VAT-backed node writes can be issued as sequential writes whose final physical mapping is recorded later.

`udf_queuebuf_seq()` classifies buffers and enqueues them for the scheduler. Reads go to the reading queue; absolute writes go to the fixed write queue; other writes go to the sequential write queue. `udf_sync_caches_seq()` asks the scheduler thread to drain and synchronize caches, then waits for completion.

The sequential write path is in `udf_issue_buf()`. It late-allocates logical space with `udf_late_allocate_buf()`, relies on linear sequential-media mapping to derive the physical block number, fixes floating descriptor tag locations, updates VAT mappings for node writes through `udf_VAT_mapping_update()`, fixes node internals, fixes FID block tag locations, and submits the buffer to the device.

`udf_doshedule()` issues one buffer from the current queue synchronously, calls the original iodone callback after completion, and switches queues only after short idle windows to avoid expensive optical read/write mode changes. When switching from reading to sequential writing, it refreshes track information. When switching back to reading, it synchronizes MMC caches. Initialization installs a `discsort` device strategy, allocates queues and descriptor pools, and starts the scheduler thread; finish stops the thread, restores the old device strategy, and frees resources.

Risk areas include synchronous scheduler behavior, unhandled write-error recovery (`panic` on write errors), VAT update correctness, and the assumption that sequential media mappings are linear. Queue switching deliberately trades latency for optical-media efficiency.
