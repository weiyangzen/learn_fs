# File Research: sources/virtualization/qemu/block/dirty-bitmap.c

Implements block dirty bitmap management around `HBitmap`. `BdrvDirtyBitmap` tracks owner BDS, bitmap storage, busy state, successor bitmap, optional name, size, disabled/readonly/persistent/inconsistent/skip-store flags, active iterators, and list linkage.

The file provides lock wrappers for `bs->dirty_bitmap_mutex`, named lookup, bitmap creation with granularity/name validation and device length sizing, lifecycle release, named bitmap release, truncate across all bitmaps, persistent bitmap driver hooks, and persistence capability checks. Successor support lets operations create an anonymous child bitmap, disable and mark the parent busy, later abdicate the name/persistence to the successor or reclaim by merging child bits back into the parent.

State APIs include enable/disable, busy, readonly, persistence, inconsistent, skip-store, query info for QMP, first/next iteration, SHA256, dirty count, granularity, and default granularity selection from cluster size clamped to 4K..64K. Iterator APIs wrap `HBitmapIter`. Dirty mutation APIs set/reset/clear/restore bits, merge bitmaps with public validation or internal unchecked paths, mark all enabled bitmaps dirty on writes, and serialize/deserialize bitmap chunks for persistence/migration.

The important invariants are: readonly bitmaps reject mutation; inconsistent persistent bitmaps are disabled and mostly unusable; active iterators prevent release; successor/busy state protects transactional replacement; cross-BDS merges lock both bitmap owners.
