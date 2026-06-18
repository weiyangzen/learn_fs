# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_group.c

## Role in the repository

`xfs_group.c` implements generic XFS group lifetime management. A group is the common abstraction behind allocation groups and realtime groups. The file manages lookup, passive references, active references, iteration, xarray insertion/removal, and group teardown.

## Reference model

Groups have two separate reference types:
- Passive references keep a group object alive for cached objects and long-lived holders. They are manipulated by `xfs_group_get`, `xfs_group_hold`, and `xfs_group_put`.
- Active references represent short-term online access to a group for walking trees or touching mutable state. They are manipulated by `xfs_group_grab`, `xfs_group_next_range`, `xfs_group_grab_next_mark`, and `xfs_group_rele`.

Active lookups use `atomic_inc_not_zero`, so a group that is being offlined or shrunk cannot be grabbed.

## Lookup and iteration

`xfs_group_get` and `xfs_group_grab` load groups from `mp->m_groups[type].xa` under RCU. `xfs_group_next_range` advances sequentially through a bounded index range, releasing the previous active reference as it moves. `xfs_group_grab_next_mark` finds the next group carrying an xarray mark, also releasing the previous active reference.

`xfs_group_get_by_fsb` maps a filesystem block to a group number for the requested group type and returns a passive reference.

## Insertion and removal

`xfs_group_insert` initializes the common group fields, optional kernel-only busy extent tracking, state lock, rmap update hooks, deferred intent drain, and the mount-owned active reference. It then inserts the group into the mount xarray.

`xfs_group_free` erases the group from the xarray, checks that passive references are gone, frees deferred drain and busy extent state, calls an optional type-specific uninit callback, drops the mount-owned active reference, checks active reference accounting, and finally frees the group via RCU-aware freeing.

## Important invariants

- The mount-owned active reference means a group is online.
- Active references must drop to zero before group memory can be freed.
- Passive references must already be cleaned up by the code responsible for cached objects.
- Iteration helpers transfer ownership by releasing the previous active reference before returning the next.
- Group xarray operations are indexed by both group number and group type.
