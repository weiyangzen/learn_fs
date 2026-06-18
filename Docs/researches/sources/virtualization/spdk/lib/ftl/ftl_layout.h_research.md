# File Research: sources/virtualization/spdk/lib/ftl/ftl_layout.h

Defines the persistent and runtime layout model for SPDK FTL metadata/data regions. The central enum `ftl_layout_region_type` assigns stable region IDs for superblock, L2P, band metadata, valid map, NV-cache metadata/data, base data, P2L checkpoints, trim metadata/logs, and P2L IO logs.

Key structures:
- `ftl_layout_region_descriptor`: persisted version, block offset, and block count.
- `ftl_layout_region`: named region with type, mirror type, current descriptor, entry geometry, VSS metadata size, and target bdev/io channel.
- `ftl_layout`: top-level geometry for base, NV cache, L2P, P2L checkpoints, all regions, and their `ftl_md` objects.
- `ftl_md_layout_ops`: device-specific hooks for region creation/open.

Important APIs cover layout setup, superblock-only setup/clear, region validation, base metadata sizing, region lookup, blob serialization/deserialization, layout offset calculation, and upgrade helpers for adding/dropping regions.

Architectural role: this header is the contract tying base-device metadata, NV-cache metadata, superblock upgrade logic, and management initialization together.
