# File Research: sources/local-fs/e2fsprogs/e2fsck/extents.c

## Purpose
Evaluates and rebuilds extent trees, including conversion from block maps to extents and optimization of overly wide/deep extent trees.

## Main Flows
- `e2fsck_rebuild_extents_later()` schedules an inode in `ctx->inodes_to_rebuild`, or rebuilds immediately if allocation is allowed.
- `load_extents()` walks an existing extent tree, frees internal extent tree blocks for later rebuild, coalesces adjacent leaf extents, and records leaf mappings.
- `find_blocks()` collects block-mapped file mappings into synthetic extents.
- `rewrite_extent_replay()` clears the inode’s extent tree, inserts extents, splits oversized initialized/uninitialized extents to legal lengths, updates quota and block counters, fixes parents, and writes the inode.
- `e2fsck_rewrite_extent_tree()` is a public rewrite helper, also used by fast-commit replay.
- `rebuild_extents()` implements pass 1E over the scheduled inode bitmap.
- `e2fsck_check_rebuild_extents()` scans an inode’s extent tree for conversion/optimization opportunities.
- `e2fsck_should_rebuild_extents()` decides whether to rebuild based on forced corruption, depth, width, and optimization settings.
- `e2fsck_pass1e()` runs pass 1E.

## Integration
Pass 1 schedules conversion/optimization through this module. Journal fast-commit replay uses `e2fsck_read_extents()` and `e2fsck_rewrite_extent_tree()` to apply extent updates.

## Risks / Notes
This module mutates allocation accounting and quota accounting while rebuilding extent metadata. Correct bitmap state and allocation permission are prerequisites.
