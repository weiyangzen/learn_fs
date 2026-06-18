# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ag_resv.h

## Purpose

This header declares the per-AG reservation API and provides the inline mapping from reservation type to the corresponding `xfs_perag` reservation structure.

## API

- Lifecycle:
  - `xfs_ag_resv_free`
  - `xfs_ag_resv_init`
- Status:
  - `xfs_ag_resv_critical`
  - `xfs_ag_resv_needed`
- Accounting hooks:
  - `xfs_ag_resv_alloc_extent`
  - `xfs_ag_resv_free_extent`
- Inline helper:
  - `xfs_perag_resv`

## Reservation Mapping

`xfs_perag_resv` maps:

- `XFS_AG_RESV_METADATA` to `pag->pag_meta_resv`
- `XFS_AG_RESV_RMAPBT` to `pag->pag_rmapbt_resv`
- all other reservation types to `NULL`

## Research Notes

This header is intentionally small but important: callers that pass reservation types into allocation/free paths rely on this mapping to find the right per-AG counters. Other reservation enum values are handled specially by implementation code rather than mapped here.
