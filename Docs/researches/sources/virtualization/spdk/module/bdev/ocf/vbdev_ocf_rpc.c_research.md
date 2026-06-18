# File Research: sources/virtualization/spdk/module/bdev/ocf/vbdev_ocf_rpc.c

This file implements JSON-RPC control surface for the SPDK OCF virtual bdev module. It registers runtime RPCs for creating and deleting OCF devices, listing OCF devices, retrieving and resetting OCF statistics, changing cache mode, setting sequential cutoff parameters, starting a cache flush, and querying flush status.

The create path decodes `name`, `mode`, optional `cache_line_size`, `cache_bdev_name`, and `core_bdev_name`, then calls `vbdev_ocf_construct()`. The asynchronous `construct_cb()` returns the created vbdev name on success or a JSON-RPC internal error on failure. Delete decodes a device name, resolves it with `vbdev_ocf_get_by_name()`, then calls `vbdev_ocf_delete_clean()` and returns a boolean from `delete_cb()`.

Statistics RPCs use a small `get_ocf_stats_ctx` containing the request and OCF core name. Both `bdev_ocf_get_stats` and `bdev_ocf_reset_stats` resolve the vbdev, take an OCF cache management read lock, operate on the named core through `vbdev_ocf_stats_get()` or `vbdev_ocf_stats_reset()`, unlock the cache, and finally either emit JSON stats or a boolean success. Error reporting converts negative OCF/SPDK-style values with `spdk_strerror(-error)`.

`bdev_ocf_get_bdevs` optionally filters by an OCF vbdev name or by cache/core base name. It emits an array of objects containing the OCF device name, started state, and nested cache/core objects with each base name and attached flag. The helper `bdev_get_bdevs_fn()` is passed to `vbdev_ocf_foreach()`.

Cache mode and sequential cutoff RPCs are thin validators around module operations. `bdev_ocf_set_cache_mode` decodes `name` and `mode`, resolves the vbdev, calls `vbdev_ocf_set_cache_mode()`, and returns the effective OCF cache mode string from `ocf_get_cache_modename(ocf_cache_get_mode())`. `bdev_ocf_set_seqcutoff` decodes policy plus optional `threshold` and `promotion_count`, then calls `vbdev_ocf_set_seqcutoff()`.

Flush handling is asynchronous and stateful on `vbdev->flush`. `bdev_ocf_flush_start` refuses detached devices, locks the OCF cache for management read, marks `flush.in_progress`, starts `ocf_mngt_cache_flush()`, and immediately returns true once the flush is submitted. The flush completion callback stores the final status and clears `in_progress`. `bdev_ocf_flush_status` returns `in_progress` and, when not in progress, the last stored status.

Important dependencies are the autogen RPC context/free helpers from `spdk_internal/rpc_autogen.h`, `vbdev_ocf` lifecycle APIs, OCF management cache locks, and the stats JSON writer. The file consistently frees decoded RPC request strings on all paths, but RPC handlers often report internal errors for decode/allocation failures rather than always using JSON-RPC invalid-params codes.
