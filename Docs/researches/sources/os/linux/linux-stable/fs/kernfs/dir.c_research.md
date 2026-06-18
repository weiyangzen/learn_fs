# File Research: sources/os/linux/linux-stable/fs/kernfs/dir.c

## Purpose

Implements kernfs directory hierarchy management: node naming/path generation, sibling indexing, active reference draining, node allocation/freeing, lookup, directory creation/removal/rename, activation/show-hide, recursive removal, self-removal, and readdir.

## Naming And Paths

- `kernfs_name()` returns a node name or `/` for root.
- `kernfs_path_from_node_locked()` constructs a path from one kernfs node to another, including relative `..` components when needed.
- `kernfs_path_from_node()` uses RCU and, unless the root has invariant parents, `kernfs_rename_lock` to stabilize parent traversal.
- `pr_cont_kernfs_name()` and `pr_cont_kernfs_path()` use a private spinlock and buffer to avoid using the global rename lock in `pr_cont()` paths.

## Tree Indexing And Lookup

Siblings are stored in an rbtree ordered by a 31-bit hash, namespace id, and name. Namespace ids use `ns_common->ns_id` instead of raw namespace pointers to avoid leaking kernel addresses. `kernfs_link_sibling()` inserts nodes, updates subdirectory counts and parent revision; `kernfs_unlink_sibling()` reverses this. Lookup helpers include `kernfs_find_ns()`, `kernfs_find_and_get_ns()`, `kernfs_walk_ns()`, and `kernfs_walk_and_get_ns()`.

## References, Activity, And Draining

- `kernfs_get()` and `kernfs_put()` manage lifetime references. Final put frees symlink target refs, xattrs, idr entries, node memory via RCU, and eventually the root.
- `kernfs_get_active()` increments the active count only if the node is not deactivated; `kernfs_put_active()` decrements and wakes waiters when deactivation completes.
- `kernfs_drain()` temporarily drops `kernfs_rwsem`, waits for active users to leave, optionally drains open files/mmaps, and reacquires locks. It is central to safe removal and hiding.

## Node Creation And Root Lifecycle

- `__kernfs_new_node()` allocates the name and node, assigns a cyclic id from the root idr, initializes ref/active state, optionally applies uid/gid iattrs, and invokes `security_kernfs_init_security()`.
- `kernfs_new_node()` handles setgid inheritance and parent reference setup.
- `kernfs_create_root()` creates a kernfs root, initializes locks/lists/idr/waitqueue, allocates the root node, and activates it unless create-deactivated mode is requested.
- `kernfs_destroy_root()` removes the root subtree and drops the root reference.
- `kernfs_create_dir_ns()` and `kernfs_create_empty_dir()` create normal and permanently empty directories.
- `kernfs_add_one()` validates namespace expectations, parent type, and removing/empty state, links the node, updates timestamps, and activates it unless the root requires explicit activation.

## VFS Directory Operations

- `kernfs_dop_revalidate()` validates positive and negative dentries against parent revision, node active state, parent identity, name, and namespace.
- `kernfs_iop_lookup()` performs namespace-aware lookup, hides inactive nodes from VFS, gets an inode for active nodes, and records parent revision on dentries.
- `kernfs_iop_mkdir()`, `kernfs_iop_rmdir()`, and `kernfs_iop_rename()` delegate to optional `kernfs_syscall_ops` callbacks while holding active references on involved nodes.
- `kernfs_dir_iops` exposes lookup, permission, setattr, getattr, listxattr, mkdir, rmdir, and rename.
- `kernfs_fop_readdir()` emits dot entries, then iterates active children in namespace/hash order using the directory position as the child hash. `file->private_data` pins the current position across calls, released by `kernfs_dir_fop_release()`.

## Activation, Hiding, And Removal

- `kernfs_activate()` walks a subtree post-order and activates nodes that were created deactivated.
- `kernfs_show()` hides or shows non-directory nodes by toggling `KERNFS_HIDDEN`; hiding deactivates and drains the node.
- `__kernfs_remove()` marks a subtree `KERNFS_REMOVING`, deactivates descendants, drains and unlinks each leftmost descendant, clears inode link counts across mounted supers, updates parent timestamps, and drops references.
- `kernfs_remove()` wraps recursive removal with `kernfs_supers_rwsem` and `kernfs_rwsem`.
- `kernfs_remove_by_name_ns()` resolves a child by name/namespace and removes it if present.
- `kernfs_remove_self()` lets a kernfs operation remove its own node by temporarily breaking active protection, arbitrating with `KERNFS_SUICIDAL/KERNFS_SUICIDED`, and making concurrent callers wait for full completion.

## Rename Semantics

`kernfs_rename_ns()` rejects root moves, inactive targets, inactive destination parents, and moves into empty directories. It optionally enforces invariant-parent roots, checks destination collisions, RCU-replaces the name if changed, updates parent under `kernfs_rename_lock` when moving across parents, recomputes the hash, relinks into the destination sibling tree, and RCU-frees the old dynamic name.

## Locking Notes

The file uses `kernfs_rwsem` for structural tree changes, `kernfs_iattr_rwsem` for iattrs/revisions/subdir counts, `kernfs_supers_rwsem` when touching mounted superblocks/inodes, `kernfs_rename_lock` for parent pointer stability, RCU for names and parent reads, and active references to keep callbacks/removal from racing. Many helpers assert the expected lock state.
