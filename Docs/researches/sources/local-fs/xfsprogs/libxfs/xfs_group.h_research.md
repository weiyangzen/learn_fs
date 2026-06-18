# File Research: sources/local-fs/xfsprogs/libxfs/xfs_group.h

## Purpose
Declares the generic `struct xfs_group` and helper APIs/macros for allocation-group or realtime-group lifetime, xarray marks, geometry conversion, and group-block verification.

## Main Contents
- `struct xfs_group`:
  - Common fields: mount pointer, group number, group type, passive refcount, active refcount.
  - Precomputed geometry: usable block count and minimum usable group block.
  - Kernel-only fields:
    - Busy extent tree or zoned RT reset list linkage.
    - Health state bitsets (`xg_checked`, `xg_sick`) protected by `xg_state_lock`.
    - Deferred intent drain used by scrub/repair to avoid transient inconsistencies.
    - Rmap update hooks for online repair.
- Reference/lifetime declarations:
  - Passive: `xfs_group_get`, `xfs_group_get_by_fsb`, `xfs_group_hold`, `xfs_group_put`.
  - Active: `xfs_group_grab`, `xfs_group_next_range`, `xfs_group_grab_next_mark`, `xfs_group_rele`.
  - Lifecycle: `xfs_group_insert`, `xfs_group_free`.
- Xarray mark macros:
  - `xfs_group_set_mark`, `xfs_group_clear_mark`, `xfs_group_marked`.
- Geometry helpers:
  - `xfs_group_max_blocks`, `xfs_groups_to_rfsbs`, `xfs_group_start_fsb`, `xfs_gbno_to_fsb`, `xfs_gbno_to_daddr`.
  - `xfs_fsb_to_gno`, `xfs_fsb_to_gbno`.
  - `xfs_verify_gbno`, `xfs_verify_gbext`.

## Dependencies and Integration
- Used by per-AG wrappers, realtime group wrappers, btree cursors, inode allocation, health tracking, and block mapping code.
- Depends on mount-level `m_groups[type]` geometry fields: `blocks`, `blklog`, `blkmask`, `start_fsb`, and `has_daddr_gaps`.

## Invariants
- `xg_active_ref` being nonzero means the group is online for active operations.
- `xg_ref` tracks passive holders that must be drained before final free.
- `xfs_gbno_to_daddr` chooses either gap-aware fsblock conversion or direct group-block multiplication based on group geometry.
- `xfs_verify_gbext` rejects zero-length extents and detects overflow when checking extent end.

## Notable Risks
- Inline conversion helpers assume mount group geometry is initialized and consistent.
- `xfs_fsb_to_gno` returns zero when `blklog` is zero, so callers must understand singleton group types.
- Kernel-only members make the same header serve userspace and kernel contexts with conditional behavior.
