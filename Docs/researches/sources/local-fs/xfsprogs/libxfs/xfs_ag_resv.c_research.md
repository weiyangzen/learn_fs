# File Research: sources/local-fs/xfsprogs/libxfs/xfs_ag_resv.c

## Role

`xfs_ag_resv.c` manages per-allocation-group block reservations for metadata structures whose future btree growth must be protected from ENOSPC. It is especially important for reflink/refcountbt and rmapbt behavior in nearly full AGs.

## Major Responsibilities

- Determine when a per-AG reservation is critically low.
- Report how many reserved blocks must remain unavailable to ordinary allocation.
- Initialize metadata and rmapbt reservations from calculated btree needs.
- Free reservations and return hidden blocks to global free-block accounting.
- Charge allocations against reservation pools or normal free-block counters.
- Return freed extents to reservation pools before normal counters.

## Reservation Model

The file describes reservations as virtual allocations maintained with incore accounting. The allocator's usable space is reduced, global `fdblocks` is adjusted, and each AG tracks remaining reserved blocks. This avoids requiring on-disk cleanup after a crash while keeping expansion space available for metadata btrees.

There are two active reservation pools:

- `XFS_AG_RESV_METADATA` for metadata btrees such as refcountbt and finobt where used blocks are already accounted as allocated, so only unused reservation is hidden.
- `XFS_AG_RESV_RMAPBT` for rmapbt blocks that live in free space, so the full reservation is hidden from `fdblocks`.

## Initialization And Freeing

`xfs_ag_resv_init` calculates metadata reservation needs with `xfs_refcountbt_calc_reserves` and `xfs_finobt_calc_reserves`, then rmapbt needs with `xfs_rmapbt_calc_reserves`. If the combined finobt/refcount reservation fails, it sets `m_finobt_nores` and retries with only refcountbt needs for backward compatibility with filesystems created before finobt reservations.

`__xfs_ag_resv_init` subtracts hidden space from `fdblocks`, adjusts `m_ag_max_usable` for AG 0, and records asked/original/current reservation values. `xfs_ag_resv_free` frees rmapbt and metadata reservations, restoring `m_ag_max_usable` for AG 0 and adding reserved blocks back to `fdblocks`.

After creating reservations, `xfs_ag_resv_init` ensures AGF data is initialized and checks that remaining reservation does not exceed AG free blocks plus AGFL blocks; if it does, it reports `-ENOSPC` while leaving policy decisions to callers.

## Allocation And Free Charging

`xfs_ag_resv_alloc_extent` handles reservation-aware allocation accounting. AGFL and metafile reservations do nothing here. Metadata/rmapbt allocations consume `ar_reserved` first; metadata allocations update reserved-freeblock accounting for reserved portions and normal freeblock accounting for any excess. Rmapbt reserved allocations do not update the superblock because their full reservation was hidden up front. Non-reserved allocations update normal freeblock counters.

`xfs_ag_resv_free_extent` refills reservation pools up to `ar_asked` before crediting normal free blocks. Rmapbt frees only refill the pool; metadata frees update reserved counters for the refilled portion and normal counters for leftovers.

## Criticality

`xfs_ag_resv_critical` treats a reservation as critically low when available blocks fall below 10 percent of the original asked amount, below maximum AG btree height, or the `XFS_ERRTAG_AG_RESV_CRITICAL` fault-injection tag triggers.

## Notable Assumptions

- Reservation type dispatch asserts on unexpected types but gracefully treats `XFS_AG_RESV_NONE` as normal accounting.
- AG 0 is used to adjust the filesystem-wide `m_ag_max_usable`, assuming it is not less hungry than other AGs.
- Initialization can intentionally leave callers with `-ENOSPC` after partial setup so higher-level grow/shrink/mount code can decide whether to continue.
