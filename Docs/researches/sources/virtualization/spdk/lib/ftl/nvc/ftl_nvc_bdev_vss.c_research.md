# File Research: sources/virtualization/spdk/lib/ftl/nvc/ftl_nvc_bdev_vss.c

Implements an NV cache backend for bdevs with separate metadata carrying VSS records.

Important behavior:
- Requires separate metadata IO, metadata size equal to `union ftl_md_vss`, DIF disabled, and zero buffer large enough for metadata transfers.
- Writes allocate metadata from `nv_cache.md_pool`, fill VSS metadata, and call `spdk_bdev_writev_blocks_with_md()`.
- On write completion, returns metadata buffer to the pool and completes the NV cache write.
- Open-chunk recovery scans chunk data up to tail metadata offset with `spdk_bdev_read_blocks_with_md()`, filters VSS entries by chunk sequence ID, and rebuilds chunk P2L mappings.

Risk:
- Metadata pool exhaustion calls `ftl_abort()`, so pool sizing is a hard correctness precondition.
