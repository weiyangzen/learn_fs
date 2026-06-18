# File Research: sources/virtualization/spdk/lib/ftl/upgrade/ftl_sb_v5.c

Implements v5 superblock blob-area storage, load, layout application, and region-upgrade bookkeeping.

Important behavior:
- Stores three blobs into the SB blob area: NVC layout tracker, base layout tracker, and layout params.
- Validates blob headers are bounded by `blob_area_end`.
- Loads blobs only if stored NVC/base device type names match the current backend names.
- Finds oldest/latest/specific region versions across NVC and base trackers.
- `ftl_superblock_v5_md_layout_upgrade_region()` handles major upgrades by deleting old region and switching to the new allocated region, or minor upgrades by rewriting version in place.
- Applies loaded layout blobs to live `dev->layout`, taking the oldest version per region type, adding placeholders for missing NVC regions, dropping deprecated `DATA_NVC`, and fixing up base-backed regions.

Risk:
- Blob bounds checks are critical; a corrupt blob header can otherwise make layout parsing unsafe.
- Device type name matching protects against applying a layout blob with an incompatible backend.
