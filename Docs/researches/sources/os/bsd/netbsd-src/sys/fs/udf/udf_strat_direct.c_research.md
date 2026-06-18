# File Research: sources/os/bsd/netbsd-src/sys/fs/udf/udf_strat_direct.c

Read completely: 457 lines.

Implements the direct UDF strategy for media where fixed-position reads and writes can be submitted directly, while still supporting delayed allocation for sequential-style data buffers. It maintains a pool of logical-block-sized node descriptor buffers in `struct strat_private`.

Node descriptor operations allocate/free descriptors from the pool, read descriptors by translating their ICB through `udf_translate_vtop()` and `udf_read_phys_dscr()`, and write descriptors to translated sectors either synchronously or asynchronously. The async node descriptor callback marks nodes modified on write error, decrements `outstanding_nodedscr`, unlocks the node when the last descriptor write completes, and releases the iobuf.

`udf_queue_buf_direct()` classifies buffers into read, fixed write, or sequential write handling. Reads and fixed writes go straight to `VOP_STRATEGY()` after descriptor/node fixups for write buffers. Sequential writes are late-allocated with `udf_late_allocate_buf()`, FID blocks and metadata bitmap tags are fixed up, node internals are fixed, logical mappings are translated to physical mappings, adjacent physical sectors are coalesced into nested buffers, and those nested writes are submitted to the device.

Initialization creates the descriptor pool; finish destroys it and frees strategy private state. `udf_sync_caches_direct()` delegates to MMC cache synchronization.

Risk areas include late allocation during queueing, fixed-vs-sequential write classification by `b_udf_c_type`, and async descriptor unlocking. The direct strategy assumes the device/media combination can tolerate direct fixed writes except where it explicitly routes delayed sequential writes.
