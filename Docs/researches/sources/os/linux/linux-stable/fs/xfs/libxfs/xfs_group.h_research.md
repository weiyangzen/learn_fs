# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_group.h

## Role in the repository

`xfs_group.h` defines the generic XFS group structure and helper APIs used by allocation groups and realtime groups. It centralizes group references, group geometry, state/health fields, deferred intent draining, rmap update hooks, xarray marks, and group-relative block conversions.

## Core structure

`struct xfs_group` contains:
- mount pointer, group number, and group type;
- passive and active reference counters;
- precomputed usable group block limits;
- kernel-only busy extent or zone-reset tracking;
- checked/sick health bitsets protected by `xg_state_lock`;
- deferred intent drain state;
- rmap update hooks for online repair.

This structure is embedded by more specific per-AG or realtime group wrappers.

## Public API

The header declares the reference and lifetime functions implemented by `xfs_group.c`:
- passive: `xfs_group_get`, `xfs_group_get_by_fsb`, `xfs_group_hold`, `xfs_group_put`;
- active: `xfs_group_grab`, `xfs_group_next_range`, `xfs_group_grab_next_mark`, `xfs_group_rele`;
- lifecycle: `xfs_group_insert`, `xfs_group_free`.

It also defines xarray mark helpers for setting, clearing, and testing group marks.

## Geometry helpers

Inline helpers convert between group-relative and filesystem-relative coordinates:
- `xfs_group_max_blocks`
- `xfs_groups_to_rfsbs`
- `xfs_group_start_fsb`
- `xfs_gbno_to_fsb`
- `xfs_gbno_to_daddr`
- `xfs_fsb_to_gno`
- `xfs_fsb_to_gbno`

`xfs_gbno_to_daddr` accounts for group types that have disk-address gaps, such as newer realtime configurations.

## Validation helpers

`xfs_verify_gbno` validates one group block number against the usable minimum and maximum. `xfs_verify_gbext` validates a nonzero extent, checks overflow, and verifies both endpoints.

## Important invariants

- Group geometry comes from `mp->m_groups[type]`; helpers are type-sensitive.
- `xg_min_gbno` and `xg_block_count` define the valid usable range, not merely the nominal group size.
- Kernel-only fields must not be assumed available in userspace libxfs builds.
- Group health bitsets require `xg_state_lock` for direct access.
