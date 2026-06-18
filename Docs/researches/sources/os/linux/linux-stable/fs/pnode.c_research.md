# File Research: sources/os/linux/linux-stable/fs/pnode.c

## Purpose

Implements VFS mount propagation logic for shared, slave, private, and unbindable mounts, including mount propagation on attach and unmount propagation.

## Main Responsibilities

- Traverses peer and slave mount propagation relationships:
  - `next_peer()`, `first_slave()`, `next_slave()`.
  - `propagation_next()`, `next_group()`, and `skip_propagation_subtree()`.
- Computes propagation metadata:
  - `get_peer_under_root()` and `get_dominating_id()` find dominating shared peer groups visible under a root.
- Changes propagation state:
  - `change_mnt_propagation()` converts mounts to shared, slave, private, or unbindable.
  - `transfer_propagation()` reparents slave lists when a mount leaves a peer group or changes master.
  - `bulk_make_private()` efficiently privatizes a set of mounts while preserving slave transfer destinations.
- Propagates new mounts:
  - `propagate_mnt()` creates secondary copies of a source mount tree for peers/slaves that should receive the mount.
  - It links new copies into the propagation graph, attaches them at `dest_mp`, and accounts them against target namespaces.
- Checks overmount and busy states:
  - `propagation_would_overmount()` determines whether a propagated mount would cover a target mount root.
  - `propagate_mount_busy()` checks whether a propagated unmount would hit busy mounts.
  - `propagate_mount_unlock()` clears `MNT_LOCKED` on propagated children when safe.
- Propagates unmount:
  - `propagate_umount()` gathers propagation recipients, trims unsafe candidates, handles locked stacks, reparents surviving overmounts, and folds acceptable candidates into the unmount set.

## Key Data/Control Flow

- Peer groups are circular `mnt_share` lists.
- Slave relationships are hlist chains under `mnt_slave_list` with `mnt_master` pointers.
- `propagate_mnt()` walks peer groups depth-first, uses `copy_tree()`, and marks masters to find the correct propagation source copies.
- Unmount propagation works in stages:
  - `gather_candidates()` finds children under propagated parents.
  - `trim_one()` removes candidates blocked by surviving submounts.
  - `handle_locked()` deals with locked chains.
  - `reparent()` moves surviving overmounts above unmounted stacks.

## Concurrency and Locking Notes

- Several functions require `namespace_sem` exclusive or shared, as documented inline.
- Unmount propagation requires `mount_lock` write seqlock and `namespace_sem` exclusive.
- Busy/unlock propagation assumes the vfsmount lock is held for write.

## Important Invariants

- Shared peer groups form contiguous segments in slave lists; traversal helpers rely on that property.
- `T_MARKED` and `T_UMOUNT_CANDIDATE` are temporary traversal markers and are cleared before returning.
- `MNT_UMOUNT` marks mounts committed to unmount.
