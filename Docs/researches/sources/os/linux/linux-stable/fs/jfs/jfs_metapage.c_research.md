# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_metapage.c

## Role

Implements JFS metadata page caching on top of Linux folios, including allocation, locking, read/write address-space operations, journal sync-list interaction, migration, release, and invalidation.

## Main Responsibilities

- Creates `jfs_mp` slab cache and mempool in `metapage_init()` and destroys them in `metapage_exit()`.
- Anchors one or more `struct metapage` objects in `folio->private`, depending on `PAGE_SIZE` versus JFS `PSIZE`.
- `__get_metapage()` locates or creates a metapage for a logical block, optionally through the direct inode mapping for absolute block access, locks it, validates size, and zeroes new metadata.
- `metapage_read_folio()` maps logical metadata blocks through `xtLookup()` and submits bios for mapped ranges.
- `metapage_write_folio()` writes dirty metapages, skips `nohomeok` pages unless force-write is set, builds contiguous bios, and manages `META_io`.
- `last_write_complete()` removes written metapages from the journal sync list when their home write completes.
- `release_metapage()` unlocks, marks dirty pages in the folio, performs synchronous write if `META_sync` is set, removes clean logged pages from log sync, and drops unused metapages.
- `force_metapage()` forces synchronous home write of a single metapage.
- `__invalidate_metapages()` marks direct-mapped metapages discarded and clears dirty/logsync state for freed extents.

## Important State

- `META_locked`: metapage-level lock separate from folio lock.
- `META_dirty`: metadata changed and must be written.
- `META_sync`: release should synchronously write.
- `META_discard`: metadata has been invalidated and must not be reused as old content.
- `META_forcewrite`: overrides `nohomeok`.
- `META_io`: home I/O is in progress.
- `nohomeok`: prevents metadata from reaching home before its journal commit makes it safe.

## Interactions

- Uses `LOGSYNC_LOCK` to remove metapages from `log->synclist`.
- Calls `jfs_flush_journal()` if writeback finds `nohomeok` pages while no group commit is active.
- Provides `jfs_metapage_aops` for metadata mappings.
- Uses `xtLookup()` for metadata file block translation, except direct/absolute mappings.

## Risk and Correctness Notes

- Folio private data differs when multiple metapages fit in one folio, requiring `meta_anchor` and I/O reference aggregation.
- Write completion avoids freeing metapages directly because the folio is not locked there.
- `__get_metapage()` treats metadata crossing a folio boundary as a hard error.
