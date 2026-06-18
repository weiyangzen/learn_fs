# File Research: sources/local-fs/xfsprogs/repair/agheader.h

## Purpose
Defines repair-side filesystem geometry comparison structures and AG header modification flags.

## Key Elements
`fs_geometry_t` mirrors key superblock geometry and feature fields used to compare candidate superblocks. It separates fields that must match automatically from fields requiring manual checks or historical tolerance.

`fs_geo_list_t` tracks geometry variants and reference counts. Defines `XR_SB_COUNTERS`, `XR_SB_INOALIGN`, and `XR_SB_SALIGN` for last-nonzero superblock field tracking, plus `XR_AG_SB`, `XR_AG_AGF`, `XR_AG_AGI`, and `XR_AG_SB_SEC` modification bits.

Provides a local inline `xfs_sb_version_hasmetadir` helper for v5 metadir feature detection from an `xfs_sb`.

## Dependencies
Uses XFS scalar types and `struct xfs_sb` feature constants from libxfs headers.

## Behavior/Risks
The geometry layout is used with `memcmp` up to `sb_shared_vn`, so field ordering is part of the comparison contract. Adding or reclassifying superblock fields requires care to preserve repair’s primary/secondary comparison semantics.
