# File Research: sources/virtualization/spdk/lib/ftl/base/ftl_base_bdev.c

## Purpose
Defines the standard base block-device type for FTL and its metadata layout operations.

## Behavior
- `is_bdev_compatible()` requires 4096-byte blocks, no separate metadata, and a write unit size of either 1 or a power of two no larger than 256 blocks.
- `md_region_setup()` initializes an `ftl_layout_region` on the base bdev with no VSS metadata.
- `md_region_create()` aligns metadata regions and reserves them through `ftl_layout_tracker_bdev_add_region()`, with data-base alignment chosen for valid-map buffer alignment.
- `md_region_open()` finds a matching region version and fills region offset, blocks, entry size, and entry count.

## Registration
Declares `base_bdev` with name `base_bdev` and registers it with `FTL_BASE_DEVICE_TYPE_REGISTER(base_bdev)`.

## Dependencies
Uses `ftl_core.h`, `ftl_layout.h`, `ftl_band.h`, and `utils/ftl_layout_tracker_bdev.h`.
