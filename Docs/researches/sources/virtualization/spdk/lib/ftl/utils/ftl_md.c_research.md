# File Research: sources/virtualization/spdk/lib/ftl/utils/ftl_md.c

Core FTL metadata object implementation, including allocation, SHM lifecycle, VSS buffers, async metadata IO, mirror handling, entry IO, clear/persist/restore, and region-specific memory flags.

Important behavior:
- Metadata buffers can be heap, SPDK DMA, or shared memory under `/dev/hugepages/ftl_<uuid>_<name>`.
- SHM creation verifies mode/size, mmaps, mlocks, and registers memory with SPDK.
- `ftl_md_create()` can allocate VSS data after data blocks and per-entry VSS DMA buffers.
- Full metadata IO is chunked by `ftl_md_xfer_blocks()` and uses SPDK bdev APIs, with NV cache wrappers when targeting the NVC bdev.
- Restore copies read data into `md->data`; persist copies from `md->data` into IO DMA buffer.
- Mirror logic persists/clears mirror first, restores from mirror on primary read failure, and resyncs mirror after dirty shutdown restore.
- Entry IO supports persisting/reading individual metadata entries with optional VSS and mirror writes.
- Region flag helpers decide SHM/SPDK/heap allocation and whether fast shutdown keeps SHM.

Risk:
- Uses `void *` pointer arithmetic in several places, relying on compiler extension.
- Many serious failures call `ftl_abort()` rather than returning errors.
- Mirror fallback reads the whole mirror, not granular ranges, as noted by TODO.
