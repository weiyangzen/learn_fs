# File Research: sources/virtualization/spdk/lib/ftl/utils/ftl_conf.c

Configuration defaults, copy/deinit, device initialization, and validation.

Behavior:
- Default config sets GC/free-band thresholds, 20% overprovisioning, 2 GiB L2P DRAM limit, user IO pool size, NV cache compaction/free targets, and fast shutdown enabled.
- `spdk_ftl_conf_copy()` deep-copies pointer strings.
- `ftl_conf_init_dev()` validates required name/base/cache fields, copies config into device, initializes limit, and registers mutable boolean properties.
- `ftl_conf_is_valid()` validates overprovisioning, NV cache thresholds, chunk target, and L2P DRAM limit.

Risk:
- `spdk_ftl_conf_deinit()` frees strings but does not null them, so callers should not reuse the struct after deinit without reinitialization.
