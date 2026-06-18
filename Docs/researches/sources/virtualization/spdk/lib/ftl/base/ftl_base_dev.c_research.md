# File Research: sources/virtualization/spdk/lib/ftl/base/ftl_base_dev.c

## Purpose
Maintains the global registry of FTL base device types.

## Behavior
- Stores registered `ftl_base_device_type` entries in a global TAILQ protected by `g_devs_mutex`.
- Validates that a type has a non-empty name.
- Rejects duplicate names with an error and `ftl_abort()`.
- `ftl_base_device_get_type_by_bdev()` iterates registered types and returns the first whose `is_bdev_compatible()` callback accepts the bdev.

## Dependencies
Uses SPDK queue/logging, pthread mutexes, `ftl_core.h`, `ftl_base_dev.h`, and `utils/ftl_defs.h`.
