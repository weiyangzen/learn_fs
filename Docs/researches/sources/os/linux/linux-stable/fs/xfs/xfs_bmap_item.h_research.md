# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_bmap_item.h

## Purpose

Defines BUI/BUD log item structures and exposes the bmap deferred update API.

## Key Contents

- `XFS_BUI_MAX_FAST_EXTENTS`
  - currently one extent per BUI.
- `struct xfs_bui_log_item`
  - BUI log item
  - refcount
  - next extent counter
  - log format
- `struct xfs_bud_log_item`
  - BUD log item
  - pointer to related BUI
  - done format
- Helpers:
  - `xfs_bui_log_item_sizeof`
  - `xfs_bmap_defer_add`
  - `xfs_bui_log_space`
  - `xfs_bud_log_space`

## Research Notes

The header documents the intent/done transaction pattern: intent items are logged before rolled work, and done items are logged with the actual bmbt updates.
