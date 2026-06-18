# File Research: sources/os/linux/linux/fs/ntfs3/bitmap.c

Read coverage: complete file, 1564 lines.

This file implements ntfs3 bitmap-window management for cluster/MFT allocation. It maintains per-window free-bit counts and two red-black trees of free extents: one ordered by start and one by length.

Key functions:
- `ntfs3_init_bitmap()` / `ntfs3_exit_bitmap()` create and destroy the `e_node` cache.
- `wnd_init()` initializes a `wnd_bitmap`, allocates per-window free counters, and scans the bitmap.
- `wnd_rescan()` reads bitmap windows from disk, populates free-bit counts, tracks total zeroes, and builds cached free extents, with support for an excluded allocation zone.
- `wnd_close()` frees counters, runlist storage, and extent tree nodes.
- `wnd_add_free_ext()` and `wnd_remove_free_ext()` maintain free-extent trees when bits are freed/allocated, merging/splitting extents and capping cached extents at `NTFS_MAX_WND_EXTENTS`.
- `wnd_set_free()`, `wnd_set_used()`, and `wnd_set_used_safe()` modify on-disk bitmap buffers and update cached counters/extents.
- `wnd_is_free()` and `wnd_is_used()` test ranges using extent caches first and falling back to bitmap reads.
- `wnd_find()` finds free space by hint, biggest extent, or bitmap scan, respecting `BITMAP_FIND_FULL`, `BITMAP_FIND_MARK_AS_USED`, and the reserved zone.
- `wnd_extend()` grows a bitmap, clears new bits, resizes counters, and adds the new free extent.
- `wnd_zone_set()` reserves or releases a zone by removing/adding it from cached free extents.
- `ntfs_trim_fs()` implements fstrim over free bitmap ranges.
- `ntfs_bitmap_set_le()`, `ntfs_bitmap_clear_le()`, and `ntfs_bitmap_weight_le()` are endian-aware bitmap primitives.

Integration:
- Used by allocation paths in `attrib.c` and broader ntfs3 cluster/MFT bitmap management.
- Maps bitmap VBOs through runlists to LBOs with `wnd_map()`, reads buffers with `ntfs_bread()`, and updates kernel buffer state.
- Calls discard/trim helpers for freed ranges and fstrim.

Risks and invariants:
- Tree cache can become approximate (`uptodated = -1`) when extent limits or allocation failures occur; scanning fallback must remain correct.
- `wnd_find()` has complex wraparound, zone exclusion, and partial-allocation behavior.
- All bitmap mutations must keep `free_bits`, `total_zeroes`, and extent trees synchronized with dirty buffer updates.
- Callers are expected to use `wnd->rw_lock`; several functions assume higher-level locking.
