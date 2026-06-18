# File Research: sources/virtualization/spdk/lib/ftl/ftl_layout.c

## Purpose
Computes, creates, loads, validates, dumps, stores, and upgrades FTL metadata/data layout regions across NV cache and base bdev.

## Region Sizing
- Superblock region size is aligned to base bdev write unit size and at least `FTL_SUPERBLOCK_SIZE`.
- Metadata region byte/block helpers align to superblock region size.
- Region names are mapped from `enum ftl_layout_region_type`.

## Setup Modes
`ftl_layout_setup()` chooses:
- `NO_RESTRICT` for create mode: creates a fresh default layout.
- `LEGACY_DEFAULT` when the superblock blob area is empty: recreates pre-v5 static layout assumptions.
- `LOAD_CURRENT` when a blob layout exists: loads and applies stored layout.

## Default Layout
- NV cache: L2P, band metadata plus mirror, P2L checkpoints, trim metadata plus mirror, trim log plus mirror, NV-cache metadata plus mirror, and NV-cache data via type-specific setup.
- Base bdev: data region and valid map.
- Superblock setup creates primary superblock on NV cache and mirror on base.

## Legacy Layout
Reopens regions using legacy versions and sizes, verifies only one matching version exists, restores legacy NV-cache chunk count, and adds placeholders for trim log regions during upgrade.

## Validation And Introspection
- `ftl_validate_regions()` rejects overlapping active regions on the same bdev.
- `ftl_layout_dump()` logs regions grouped by NV cache and base device.
- `ftl_layout_base_md_blocks()` estimates base metadata footprint for valid map and superblock.

## Blob Support
`ftl_layout_blob_store()` serializes region type, entry size, and entry count. `ftl_layout_blob_load()` validates blob size/type and restores those fields. `ftl_layout_upgrade_add_region_placeholder()` marks missing upgrade regions as placeholders.

## Dependencies
Uses SPDK bdev APIs, FTL core/utils/band/layout/NV-cache/superblock, NV-cache device ops, bdev layout tracker, and layout upgrade helpers.
