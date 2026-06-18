# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_ag_resv.h

Declares XFS per-AG reservation APIs.

Key behavior:
- Exposes reservation lifecycle:
  - `xfs_ag_resv_init`.
  - `xfs_ag_resv_free`.
- Exposes reservation state queries:
  - `xfs_ag_resv_critical`.
  - `xfs_ag_resv_needed`.
- Exposes accounting hooks for allocation and free paths:
  - `xfs_ag_resv_alloc_extent`.
  - `xfs_ag_resv_free_extent`.
- Provides `xfs_perag_resv` inline mapper:
  - `XFS_AG_RESV_METADATA` maps to `pag_meta_resv`.
  - `XFS_AG_RESV_RMAPBT` maps to `pag_rmapbt_resv`.
  - other reservation types return `NULL`.

Important interactions:
- Included by allocator, AG grow/shrink code, and metadata btree code that must account against per-AG reservations.
