# File Research: sources/virtualization/spdk/lib/ftl/base/ftl_base_dev.h

## Purpose
Declares the plugin interface for FTL base-device types.

## Key Types
- `struct ftl_base_device_ops`: compatibility callback plus `ftl_md_layout_ops`.
- `struct ftl_base_device_type`: name, ops, and TAILQ entry.

## API
- `FTL_BASE_DEVICE_TYPE_REGISTER(desc)` registers a base device type through a constructor.
- `ftl_base_device_register()` adds a descriptor to the registry.
- `ftl_base_device_get_type_by_bdev()` selects a registered type for an SPDK bdev.

## Dependencies
Includes SPDK stdinc, bdev module APIs, queues, and `ftl_layout.h`.
