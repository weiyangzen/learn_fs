# File Research: sources/local-fs/kdave-linux/fs/btrfs/subpage.c

Read coverage: complete file, 828 lines.

This file implements Btrfs subpage folio state: tracking sector-level uptodate, dirty, writeback, ordered, checked, and locked bits when filesystem sector size is smaller than folio/page size.

Main responsibilities:
- Allocates and attaches `struct btrfs_folio_state` as folio private data for metadata or data folios.
- Maintains packed per-sector bitmaps for page state flags.
- Provides subpage-aware set, clear, test, clamp, and metadata wrappers.
- Bridges normal folio flags and subpage bitmaps so non-subpage filesystems use standard folio operations.
- Manages subpage locking for compressed async delalloc and multi-sector folios.
- Provides debug dumping and dirty bitmap extraction.

Important flows:
- `btrfs_attach_folio_state()` attaches private state only when subpage handling is needed.
- `btrfs_alloc_folio_state()` sizes the bitmap array as `bitmap_count * blocks_per_folio`.
- `btrfs_folio_inc_eb_refs()` and `btrfs_folio_dec_eb_refs()` protect metadata extent-buffer lifetime against folio-private detachment races.
- `btrfs_folio_set_lock()`, `btrfs_folio_end_lock()`, and `btrfs_folio_end_lock_bitmap()` maintain subpage lock counts and unlock the folio only after the last locked sector clears.
- Explicit implementations handle uptodate, dirty, writeback, ordered, and checked state.
- `IMPLEMENT_BTRFS_PAGE_OPS()` generates regular, clamped, and metadata wrappers for each tracked state.
- `btrfs_meta_folio_clear_and_test_dirty()` tells metadata writeback whether clearing an extent buffer made the whole folio clean.
- `btrfs_folio_assert_not_dirty()` and `btrfs_subpage_dump_bitmap()` support assert/debug diagnostics.

Concurrency and invariants:
- `btrfs_folio_state->lock` protects bitmap operations.
- Data folios use `nr_locked`; metadata folios use `eb_refs` in the same union.
- Metadata subpage support asserts non-large folios.
- Range operations assert sector alignment and single-folio containment, except clamp helpers intentionally trim ranges.
- Writeback start preserves the `TOWRITE` tag when the folio remains dirty to avoid sync writeback ordering bugs.

Integration points:
- Used by extent buffer, extent IO, delalloc, metadata writeback, and data folio code.
- Depends on `btrfs_blocks_per_folio()`, folio flags, extent buffer ranges, and `is_data_inode()` assertions.

Risk notes:
- Bitmap/folio flag synchronization is subtle; a missed clear can leave folios permanently dirty/writeback/ordered.
- Lock count handling must remain consistent with bitmap bits or folio unlock can happen too early or never happen.
- Metadata subpage behavior intentionally avoids page locking as the sole metadata lock to prevent deadlocks among tree blocks sharing a folio.
