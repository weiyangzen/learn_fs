# File Research: sources/local-fs/xfsprogs/libxfs/xfs_group.c

## Purpose
Implements the generic XFS group lifetime and lookup abstraction used for allocation groups and realtime groups. Groups are stored in mount-level xarrays and use separate passive and active reference counts.

## Main Functions
- `xfs_group_get`:
  - RCU-loads a group by index/type from `mp->m_groups[type].xa`.
  - Takes a passive reference if found.
- `xfs_group_hold`:
  - Takes another passive reference from an existing group pointer.
  - Requires either passive or active refs already exist.
- `xfs_group_put`:
  - Drops a passive reference.
- `xfs_group_grab`:
  - RCU-loads a group and attempts to take an active reference via `atomic_inc_not_zero`.
  - Fails if the group is being offlined/shrunk and active refs are zero.
- `xfs_group_next_range`:
  - Iterates through a numeric group range, releasing the previous active ref and grabbing the next group.
- `xfs_group_grab_next_mark`:
  - Iterates to the next xarray entry with a specified mark, taking an active reference.
- `xfs_group_rele`:
  - Drops an active reference.
- `xfs_group_insert`:
  - Initializes mount/index/type, kernel-only busy extent or hook state, defer-drain state, and sets the mount-owned active reference.
  - Inserts the group into the mount xarray.
- `xfs_group_free`:
  - Removes the group from the xarray, checks passive refs are gone, frees drain/busy state, runs optional uninit, drops mount active ref, verifies active refs are zero, and RCU-frees.
- `xfs_group_get_by_fsb`:
  - Converts a filesystem block to group number and takes a passive reference.

## Dependencies and Integration
- Uses xarray APIs, RCU read-side protection, atomics, tracing, defer-drain infrastructure, and kernel-only extent busy/rmap hook structures.
- `xfs_group.h` supplies the structure and conversion helpers.
- Mount geometry in `mp->m_groups[type]` defines group block/log/mask parameters.

## Invariants and Control Flow
- Passive refs protect longer-lived cached holders; the freeing path is responsible for cleaning those holders before `xfs_group_free`.
- Active refs represent online usability; a mount-owned active ref keeps the group online.
- Removing/offlining a group prevents new active refs because `atomic_inc_not_zero` fails once active refs reach zero.
- Iterators transfer active references by releasing the previous group before grabbing the next.

## Notable Risks
- `xfs_group_free` assumes `xa_erase` returns a valid group; callers must ensure the xarray entry exists.
- Consumers that break out of `xfs_group_next_range` or marked iteration early must release the active ref themselves.
- Passive ref misuse can leave cached objects pointing at groups past the intended cleanup point.
