# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_extended_slotmap.c

## Purpose
Toggles the extended slot map incompat feature.

## Main Behavior
- `enable_extended_slotmap()`:
  - No-ops if extended slot map is already in use.
  - Sets `OCFS2_FEATURE_INCOMPAT_EXTENDED_SLOT_MAP`.
  - Calls `ocfs2_format_slot_map()` to rewrite the slot map in the new format.
  - Writes the superblock.
- `disable_extended_slotmap()`:
  - No-ops if old-style slot map is already in use.
  - Clears the feature bit.
  - Calls `ocfs2_format_slot_map()` to rewrite old-style slot map data.
  - Writes the superblock.
- Defines `extended_slotmap_feature` with `TUNEFS_FLAG_RW | TUNEFS_FLAG_ALLOCATION`.

## Dependencies
- OCFS2 slot map formatting and feature helpers.
- Tunefs signal and progress helpers.

## Notes
The feature bit is changed before formatting so `ocfs2_format_slot_map()` sees the target layout.
