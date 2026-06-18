# File Research: sources/local-fs/xfsprogs/libxfs/xfs_ag_resv.h

## Role

`xfs_ag_resv.h` declares the per-AG reservation interface used by allocation and AG management code.

## Interface

- `xfs_ag_resv_free` releases both metadata and rmapbt reservations for an AG.
- `xfs_ag_resv_init` calculates and creates reservations for an AG.
- `xfs_ag_resv_critical` reports whether a reservation pool is dangerously low.
- `xfs_ag_resv_needed` returns reserved blocks that must be withheld from ordinary allocation.
- `xfs_ag_resv_alloc_extent` charges an allocation to a reservation or normal accounting.
- `xfs_ag_resv_free_extent` returns freed blocks to a reservation or normal accounting.
- `xfs_perag_resv` maps `XFS_AG_RESV_METADATA` and `XFS_AG_RESV_RMAPBT` to the corresponding fields inside `struct xfs_perag`.

## Notable Assumptions

`xfs_perag_resv` returns `NULL` for unsupported reservation types; callers in `xfs_ag_resv.c` validate types before dereferencing. The header depends on `struct xfs_perag`, `struct xfs_trans`, `struct xfs_alloc_arg`, and reservation enum definitions supplied by surrounding libxfs headers.
