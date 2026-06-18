# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_group.h

## Purpose

`xfs_group.h` declares the generic XFS group object and helper APIs used for allocation groups and realtime groups. It also provides group-local geometry conversion and extent validation helpers.

## Main Content

- Defines `struct xfs_group`:
  - Mount pointer, group number, group type.
  - Passive and active reference counts.
  - Precomputed usable block bounds: `xg_block_count` and `xg_min_gbno`.
  - Kernel-only busy extent or zoned reset list state.
  - Kernel-only health state, state lock, defer-intent drain, and rmap update hooks.
- Declares group reference and lifecycle functions implemented in `xfs_group.c`.
- Defines xarray mark helpers:
  - `xfs_group_set_mark`.
  - `xfs_group_clear_mark`.
  - `xfs_group_marked`.
- Defines geometry helpers:
  - `xfs_group_max_blocks`.
  - `xfs_groups_to_rfsbs`.
  - `xfs_group_start_fsb`.
  - `xfs_gbno_to_fsb`.
  - `xfs_gbno_to_daddr`.
  - `xfs_fsb_to_gno`.
  - `xfs_fsb_to_gbno`.
- Defines group block validation:
  - `xfs_verify_gbno`.
  - `xfs_verify_gbext`.

## Key Interfaces and Invariants

- `xfs_gbno_to_daddr` handles both dense group address spaces and groups with disk-address gaps.
- `xfs_verify_gbno` enforces both upper bound and minimum usable block bound.
- `xfs_verify_gbext` rejects zero-length extents and catches arithmetic overflow before validating the end block.
- Kernel-only health fields (`xg_checked`, `xg_sick`) are shared with the health tracking API in `xfs_health.h`.

## Dependencies

Requires XFS mount group geometry (`mp->m_groups[type]`), xarray marks, atomic counters, and kernel-only XFS infrastructure when compiled in kernel mode.
