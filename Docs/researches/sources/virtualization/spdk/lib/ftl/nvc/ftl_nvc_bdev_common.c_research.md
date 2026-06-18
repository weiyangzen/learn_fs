# File Research: sources/virtualization/spdk/lib/ftl/nvc/ftl_nvc_bdev_common.c

Common helpers for NV cache bdev device types.

Functions:
- `ftl_nvc_bdev_common_is_chunk_active()` dry-runs an insert into the NVC layout tracker to determine whether a chunk-sized range is free/usable.
- `ftl_nvc_bdev_common_region_create()` aligns metadata region size and adds it to the NVC layout tracker.
- `ftl_nvc_bdev_common_region_open()` finds a region of a requested type/version and fills an `ftl_layout_region` descriptor with bdev descriptor, IO channel, VSS size, entry size/count, offset, size, and version.

Risk:
- `region_open()` accepts an existing region if `blk_sz >= requested`, so callers must tolerate larger backing regions.
