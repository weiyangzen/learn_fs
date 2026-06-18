# File Research: sources/os/linux/linux/fs/pnode.c

## Purpose
Implements mount propagation mechanics for shared, slave, private, and unbindable mounts. This file maintains propagation relationships between mount peer groups and handles propagation during mount attachment and unmount operations.

## Main Responsibilities
- Finds peer and slave mounts in propagation trees.
- Changes mount propagation type via `change_mnt_propagation()`.
- Converts groups of mounts to private with `bulk_make_private()`.
- Creates propagated secondary mount copies with `propagate_mnt()`.
- Checks whether propagation would overmount a mount with `propagation_would_overmount()`.
- Determines propagated unmount busy state and unlock behavior.
- Expands an unmount set according to propagation rules with `propagate_umount()`.

## Key Interfaces
- `get_dominating_id()`
- `change_mnt_propagation()`
- `bulk_make_private()`
- `propagate_mnt()`
- `propagation_would_overmount()`
- `propagate_mount_busy()`
- `propagate_mount_unlock()`
- `propagate_umount()`

## Control Flow and Algorithms
The file models peer groups as circular `mnt_share` lists and slave relationships as hlist chains. Propagation walks use helpers such as `propagation_next()`, `skip_propagation_subtree()`, and `next_group()` to traverse peer/slave hierarchies while respecting mounts newly created by propagation.

`propagate_mnt()` walks peer groups depth-first, determines whether secondary copies are needed, copies source trees with the right clone flags, attaches copies at the destination mountpoint, and records them in `tree_list`.

`propagate_umount()` first gathers propagated unmount candidates, trims candidates that would reveal covered mounts or violate locked mount constraints, handles locked chains, reparents surviving overmounts, and finally folds valid propagated unmounts into the caller’s set.

## Dependencies and Integration
Uses `struct mount`, `struct mountpoint`, namespace state, mount locks, `copy_tree()`, `count_mounts()`, mountpoint manipulation helpers, and propagation flags from `pnode.h`/mount internals. It is tightly integrated with namespace locking and VFS mount/unmount code.

## Concurrency and Lifetime Notes
Comments document required locks: many paths require `namespace_sem`, and unmount checks require `mount_lock` write protection. The implementation mutates shared/slave lists and temporary mount flags (`T_MARKED`, `T_UMOUNT_CANDIDATE`), so correct cleanup of marks is critical.

## Risks and Review Hotspots
- Propagation tree traversal is subtle; incorrect peer/slave ordering can duplicate, miss, or wrongly attach mounts.
- Temporary flags must be cleared on all paths to avoid corrupting later propagation operations.
- Unmount candidate trimming has security and namespace visibility implications, especially around locked mounts and overmount chains.
- `propagate_mnt()` error handling must leave copied mount trees and marks in a state expected by callers.
