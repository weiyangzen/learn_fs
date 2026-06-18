# File Research: sources/local-fs/kdave-linux/fs/btrfs/subpage.h

Read coverage: complete file, 212 lines.

This header declares Btrfs subpage folio-state types and helper APIs.

Main contents:
- Bitmap index enum for `uptodate`, `dirty`, `writeback`, `ordered`, `checked`, and `locked`.
- `struct btrfs_folio_state`, containing a spinlock, either metadata `eb_refs` or data `nr_locked`, and flexible packed bitmap storage.
- `enum btrfs_folio_type` distinguishes metadata and data users.
- Inline detection helpers:
  - `btrfs_meta_is_subpage()` checks `nodesize < PAGE_SIZE`.
  - `btrfs_is_subpage()` checks `sectorsize < folio_size(folio)` and asserts data inode mapping when present.

Declared API:
- Attach/detach/allocation: `btrfs_attach_folio_state()`, `btrfs_detach_folio_state()`, `btrfs_alloc_folio_state()`, `btrfs_free_folio_state()`.
- Metadata extent-buffer refs: `btrfs_folio_inc_eb_refs()`, `btrfs_folio_dec_eb_refs()`.
- Lock handling: `btrfs_folio_set_lock()`, `btrfs_folio_end_lock()`, `btrfs_folio_end_lock_bitmap()`.
- Macro-generated state APIs for subpage, regular folio, clamped folio, and metadata folio operations.
- Cleanup/debug helpers: `btrfs_folio_clamp_finish_io()`, dirty clear/test helpers, dirty assertions, dirty bitmap extraction, and bitmap dump.

Design notes:
- The header documents the naming split:
  - `btrfs_subpage_*()` assumes subpage private state and a range inside one folio.
  - `btrfs_folio_*()` handles either subpage or normal folio.
  - `btrfs_folio_clamp_*()` trims larger ranges to a folio.
  - `btrfs_meta_folio_*()` is for metadata extent buffers.

Risk notes:
- Callers must choose the correct helper family; passing a cross-folio range to non-clamp helpers violates assumptions.
- Ordered and checked flags are documented as deprecated COW-fixup state.
- The locked bitmap is tied to async delalloc/compression lifetime and is explicitly marked as needing future rework.
