# File Research: sources/virtualization/spdk/module/bdev/ocf/vbdev_ocf.c

This file is the main OCF virtual bdev implementation. It registers the `ocf` bdev module, manages OCF cache/core devices, exposes a cached bdev, drives OCF I/O queues with SPDK pollers, handles async management paths, supports hotremove and examine-time construction/loading, and coordinates clean versus dirty deletion.

Global state tracks all configured/running OCF vbdevs, bdevs currently delaying examine completion, and whether module finalization has started. Each `vbdev_ocf` owns cache/core base descriptors, OCF cache/core handles, OCF config, state flags, a management context, an exposed SPDK bdev, cache context, and UUID metadata used to identify the core/cache/vbdev tuple.

Construction begins with `vbdev_ocf_construct()`, which allocates the vbdev, initializes OCF configs/defaults, encodes cache/core volume UUIDs, validates cache mode and cache line size, attaches any already-present base bdevs, and registers the vbdev once both cache and core are available. Base attach opens bdevs writable, claims them for the OCF module, obtains management channels, records the opening thread, and shares an already-open cache base among vbdevs that use the same cache device.

Registration is a management path: start or reuse an OCF cache, create a management queue, attach or load the cache device, add the core, then construct/register the exported SPDK bdev and io_device. The exposed bdev copies core block length, block count, write-cache flag, alignment, NUMA node, and derives a UUID from a fixed namespace UUID plus the core bdev UUID. OCF queues are created per SPDK I/O channel and driven by pollers that run up to 32 pending OCF requests per poll.

The I/O path supports read, write, flush, and unmap if the core bdev supports them. Reads allocate a buffer first if needed. `io_handle()` maps bdev offsets/lengths to an OCF volume I/O, converts the SPDK driver context into OCF data, sets completion, and submits read/write/flush/discard to OCF. OCF completion maps success, no-memory, and failure to SPDK bdev I/O statuses and releases the OCF I/O.

Deletion has two explicit paths. Dirty unregister flushes, stops the cache, detaches/closes cache, detaches/closes core, then finishes, preserving metadata for future recovery. Clean delete flushes, removes/detaches core first, then stops/detaches cache, making the instance permanent removal. Destruct is asynchronous for started bdevs via `spdk_io_device_unregister()` and delayed `spdk_bdev_destruct_done()`.

Examine handling serves both config-created devices waiting for base bdevs and metadata-probe discovery. `examine_config` attaches matching base devices as they appear. `examine_disk` delays module examine completion, starts configured vbdevs when both bases are present, or opens an unconfigured bdev as a temporary OCF volume and calls `ocf_metadata_probe()` to check for existing OCF metadata. The metadata-probe callback currently just handles status/cleanup in this file.

Hotremove unregisters affected OCF vbdevs. Removing a core deletes only its parent. Removing a cache walks all vbdevs using that cache name and deletes them. Base descriptors are closed on their original opening threads when necessary.

Control operations include cache mode update and sequential cutoff policy/threshold/promotion-count updates under OCF cache trylock. JSON dump/config reports cache/core names, cache mode, cache line size, and volatile metadata flag. Important invariants are single active management operation per vbdev, OCF cache locking around management mutations, reference sharing for reused cache instances, correct clean/dirty removal ordering, and per-channel OCF queue lifetime during io_device destroy.
