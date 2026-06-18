# File Research: sources/virtualization/spdk/lib/ftl/utils/ftl_layout_tracker_bdev.c

Implements a block-device region tracker for metadata layout allocation.

Behavior:
- Initializes with one free region covering the full bdev.
- Adds regions by best-fit free region, with optional block alignment and splitting.
- Inserts regions at exact block offsets, also supporting dry-run with `FTL_LAYOUT_REGION_TYPE_INVALID`.
- Removes regions and coalesces adjacent free regions.
- Iterates regions by type, or all regions with invalid type filter.
- Serializes allocated regions only into packed blob entries.
- Loads blob entries by resetting the tracker and exact-inserting each allocated region.

Risk:
- `blob_store()` checks capacity before skipping free entries, so many free entries can falsely exhaust a small blob buffer even though they are not serialized.
- Exact insert and remove rely on duplicate `(type, version)` being disallowed, not duplicate physical ranges alone.
