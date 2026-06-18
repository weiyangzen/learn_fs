# File Research: sources/virtualization/spdk/lib/ftl/ftl_sb.c

Dispatches superblock operations by on-disk superblock version.

`struct sb_ops` contains version-specific hooks for magic validation, blob-area checks/load/store, region upgrade, layout apply, and layout dump. `sb_get_ops` maps versions 0-5:
- v0-v2 use legacy v2 magic checks.
- v3-v4 use v3 magic and v3 layout blob load/dump.
- v5 uses v3 magic plus v5 blob validation/store/load, region upgrade, layout apply, and dump.

Exported functions are thin dispatchers:
- `ftl_superblock_check_magic`
- `ftl_superblock_is_blob_area_empty`
- `ftl_superblock_validate_blob_area`
- `ftl_superblock_store_blob_area`
- `ftl_superblock_load_blob_area`
- `ftl_superblock_md_layout_upgrade_region`
- `ftl_superblock_md_layout_apply`
- `ftl_superblock_md_layout_dump`

Unsupported missing mandatory ops generally abort; optional validation/apply can default to success.
