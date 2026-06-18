# File Research: sources/local-fs/xfsprogs/libxfs/xfs_alloc.h

## Purpose

`xfs_alloc.h` declares the public allocation/free-space API for libxfs allocation-group management. It exposes allocation arguments, allocator flags, free-space btree query helpers, AGF/AGFL accessors, deferred extent-free interfaces, and allocation cache lifecycle hooks.

## Key Types

- `struct xfs_alloc_arg`: central argument/result carrier for allocation routines. It includes transaction, mount, AGF buffer, perag, target fsblock/AG/AG block, min/max/prod/mod/alignment constraints, minleft/total reservation pressure, NEAR allocation AG block bounds, output length, allocation datatype, delayed-allocation hints, freelist source flag, exact-minlen debug flag, owner info, and AG reservation type.
- `struct xfs_extent_free_item`: deferred free work item sorted by start block. It records owner, start block, block count, group, flags, and AG reservation.
- `struct xfs_alloc_autoreap`: handle for a paused deferred free pending item used to autoreap allocations if a later operation fails or recovery completes it.
- `xfs_alloc_query_range_fn` and `xfs_agfl_walk_fn`: callbacks for btree free-space record queries and AGFL walks.

## Flags and Constants

Freelist fix flags:
- `XFS_ALLOC_FLAG_TRYLOCK`: trylock buffer reads.
- `XFS_ALLOC_FLAG_FREEING`: caller is freeing extents.
- `XFS_ALLOC_FLAG_NORMAP`: do not update rmapbt.
- `XFS_ALLOC_FLAG_NOSHRINK`: do not shrink AGFL.
- `XFS_ALLOC_FLAG_CHECK`: test only; do not modify allocation args.
- `XFS_ALLOC_FLAG_TRYFLUSH`: avoid waiting in busy extent flush.

Allocation datatype flags:
- `XFS_ALLOC_USERDATA`
- `XFS_ALLOC_INITIAL_USER_DATA`
- `XFS_ALLOC_NOBUSY`

Deferred free flags:
- `XFS_FREE_EXTENT_SKIP_DISCARD`
- `XFS_FREE_EXTENT_REALTIME`
- `XFS_FREE_EXTENT_ALL_FLAGS`

Extent free item flags:
- `XFS_EFI_SKIP_DISCARD`
- `XFS_EFI_ATTR_FORK`
- `XFS_EFI_BMBT_BLOCK`
- `XFS_EFI_CANCELLED`
- `XFS_EFI_REALTIME`

## Exported Allocation and Free APIs

- `xfs_alloc_vextent_this_ag`
- `xfs_alloc_vextent_near_bno`
- `xfs_alloc_vextent_exact_bno`
- `xfs_alloc_vextent_start_ag`
- `xfs_alloc_vextent_first_ag`
- `__xfs_free_extent`
- `xfs_free_extent` inline wrapper with discard enabled by default
- `xfs_free_ag_extent`
- `xfs_free_extent_later`
- `xfs_free_extent_fix_freelist`

These entry points cover allocation within one AG, allocation near/exact targets, whole-filesystem fallback scans, immediate frees, and deferred frees.

## Exported Metadata Helpers

- `xfs_agfl_size`, `xfs_alloc_set_aside`, `xfs_alloc_ag_max_usable`, `xfs_prealloc_blocks`
- `xfs_alloc_longest_free_extent`, `xfs_alloc_min_freelist`
- `xfs_alloc_compute_maxlevels`
- `xfs_alloc_log_agf`
- `xfs_read_agf`, `xfs_alloc_read_agf`, `xfs_alloc_read_agfl`
- `xfs_alloc_fix_freelist`
- `xfs_alloc_get_freelist`, `xfs_alloc_put_freelist`
- `xfs_validate_ag_length`

## Btree Query and Record Helpers

- `xfs_alloc_lookup_le`, `xfs_alloc_lookup_ge`, `xfs_alloc_get_rec`
- `xfs_alloc_btrec_to_irec`
- `xfs_alloc_check_irec`
- `xfs_alloc_query_range`, `xfs_alloc_query_all`
- `xfs_alloc_has_records`
- `xfs_agfl_walk`
- `xfs_buf_to_agfl_bno` inline helper returns the AGFL block-number array start, skipping the v5 AGFL header on CRC filesystems.

## Autoreap and Cache Lifecycle

- `xfs_alloc_schedule_autoreap`, `xfs_alloc_cancel_autoreap`, `xfs_alloc_commit_autoreap`
- `xfs_extfree_intent_init_cache`, `xfs_extfree_intent_destroy_cache`
- `xfs_extfree_item_cache` exported cache pointer.
- `xfs_alloc_wq` exported workqueue pointer.

## Integration Notes

This header is consumed by allocation btree code, bmap code, transaction/defer code, repair code, and scrub/query paths. `NORMAP` and `NOSHRINK` are explicitly documented as repair-oriented flags, which is important because this file lives in shared libxfs rather than only kernel XFS.
