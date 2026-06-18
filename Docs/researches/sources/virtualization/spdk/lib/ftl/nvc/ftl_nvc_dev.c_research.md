# File Research: sources/virtualization/spdk/lib/ftl/nvc/ftl_nvc_dev.c

Global registry for NV cache device types.

Behavior:
- Maintains a TAILQ protected by `g_devs_mutex`.
- `ftl_nv_cache_device_register()` validates name and rejects duplicate names by aborting.
- `ftl_nv_cache_device_get_type_by_bdev()` iterates registered types and returns the first whose `is_bdev_compatible()` accepts the bdev.

Risk:
- Selection order is constructor registration order; compatibility predicates must be mutually exclusive or intentionally prioritized.
