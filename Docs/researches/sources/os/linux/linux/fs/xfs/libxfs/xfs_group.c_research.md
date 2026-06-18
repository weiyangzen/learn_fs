# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_group.c

## Purpose

`xfs_group.c` implements generic XFS group lifetime and lookup support. A group is an abstraction for allocation groups and realtime groups, stored in mount-level xarrays and protected by passive and active reference counts.

## Main Content

- Implements passive reference helpers:
  - `xfs_group_get` looks up a group by index/type under RCU and increments `xg_ref`.
  - `xfs_group_hold` increments a passive ref on an existing group.
  - `xfs_group_put` decrements a passive ref.
- Implements active reference helpers:
  - `xfs_group_grab` looks up a group and increments `xg_active_ref` only if nonzero.
  - `xfs_group_rele` decrements the active ref.
  - Active refs are intended for short-lived operational access and fail if a group is being removed/offlined.
- Implements iteration:
  - `xfs_group_next_range` walks sequential group indices in a bounded range.
  - `xfs_group_grab_next_mark` finds the next group marked in the xarray.
- Implements insertion and removal:
  - `xfs_group_insert` initializes group identity, optional extent-busy tracking, kernel-only state locks/hooks, defer drains, and the mount-owned active reference before inserting into the mount xarray.
  - `xfs_group_free` erases the group from the xarray, validates passive refs are gone, drains deferred intents, releases kernel-only resources, calls optional uninit, drops the mount active ref, validates active refs, and frees via RCU.
- Provides `xfs_group_get_by_fsb`, mapping a filesystem block to group number before lookup.

## Key Interfaces and Invariants

- Passive refs protect long-lived objects that can be cleaned up during group teardown.
- Active refs represent online/access-safe group use. A zero active count means new active users cannot enter.
- The mount holds one active reference to indicate that the group is online.
- `xfs_group_free` expects no passive references and no active references after dropping the mount ref.
- The xarray under `mp->m_groups[type].xa` is the authoritative group index.

## Dependencies

Includes core XFS mount, error, trace, extent busy, and defer-drain infrastructure. Kernel-only portions allocate extent busy trees, initialize spinlocks/hooks, and free kernel resources.
