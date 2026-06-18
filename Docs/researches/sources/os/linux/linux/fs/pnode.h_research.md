# File Research: sources/os/linux/linux/fs/pnode.h

## Purpose
Internal header for mount propagation support. It defines propagation state predicates, clone flags, and prototypes used by mount namespace code and `pnode.c`.

## Main Contents
- Mount state macros:
  - `IS_MNT_SHARED`
  - `IS_MNT_SLAVE`
  - `IS_MNT_NEW`
  - `IS_MNT_UNBINDABLE`
  - `IS_MNT_MARKED`
  - `IS_MNT_LOCKED`
- Mutation helpers:
  - `CLEAR_MNT_SHARED`
  - `SET_MNT_MARK`
  - `CLEAR_MNT_MARK`
  - `set_mnt_shared()`
- Clone flags:
  - `CL_EXPIRE`
  - `CL_SLAVE`
  - `CL_COPY_UNBINDABLE`
  - `CL_MAKE_SHARED`
  - `CL_PRIVATE`
  - `CL_COPY_MNT_NS_FILE`
- Peer predicate: `peers()` checks nonzero matching mount group IDs.

## Exposed Interfaces
Declares the propagation functions implemented in `pnode.c` plus cross-file mount helpers such as `mnt_release_group_id()`, `mnt_get_count()`, `mnt_set_mountpoint()`, `mnt_change_mountpoint()`, `copy_tree()`, `is_path_reachable()`, and `count_mounts()`.

## Dependencies and Integration
Includes `linux/list.h` and internal `mount.h`. It is an internal VFS mount header, not a user-facing API.

## Risks and Review Hotspots
- Macros directly inspect and mutate mount flags; callers must hold the correct locks.
- `peers()` treats group ID zero as non-peer even if IDs match, which is essential for private/non-shared mounts.
- Clone flag values are consumed by tree-copying and propagation logic; changing them affects mount namespace semantics.
