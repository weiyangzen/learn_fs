# File Research: sources/os/linux/linux/fs/kernfs/dir.c

kernfs directory and hierarchy implementation: node naming, path construction, sibling indexing, active-reference lifetime, creation, removal, rename, lookup, and readdir.

Key responsibilities:
- Provides name/path helpers: `kernfs_name()`, `kernfs_path_from_node()`, `pr_cont_kernfs_name()`, and `pr_cont_kernfs_path()`.
- Computes common ancestors and relative paths under RCU and rename locking.
- Hashes and compares sibling names with namespace IDs while avoiding kernel pointer exposure.
- Maintains parent child sets as rbtrees through `kernfs_link_sibling()` and `kernfs_unlink_sibling()`.
- Manages active references with `kernfs_get_active()`, `kernfs_put_active()`, and `kernfs_drain()`.
- Manages base references and RCU freeing with `kernfs_get()`, `kernfs_put()`, and `kernfs_free_rcu()`.
- Allocates nodes through `__kernfs_new_node()` and `kernfs_new_node()`, including IDR inode IDs, inherited gid/setgid behavior, and security initialization.
- Supports ID lookup through `kernfs_find_and_get_node_by_id()`.
- Adds nodes through `kernfs_add_one()` and supports namespace-aware find/walk helpers.
- Creates and destroys roots with `kernfs_create_root()` and `kernfs_destroy_root()`.
- Creates regular directories and permanently empty directories.
- Implements VFS dentry revalidation, lookup, mkdir/rmdir/rename syscall forwarding, directory inode operations, and directory file operations.
- Activates subtrees, hides/shows non-directory nodes, recursively removes subtrees, removes by name, supports self-removal from active operations, and renames/moves nodes.
- Implements stable-ish directory iteration using per-child hash values as `ctx->pos`.

Important interactions:
- Uses root-level locks: `kernfs_rwsem`, `kernfs_iattr_rwsem`, `kernfs_supers_rwsem`, `kernfs_rename_lock`, and `kernfs_idr_lock`.
- Integrates with kernfs inode, file, symlink, mount, xattr, mmap-drain, and syscall operation hooks from `kernfs-internal.h`.
- Calls LSM hook `security_kernfs_init_security()`.
- Uses VFS dentry/inode operations, fsnotify-relevant link clearing, and `dir_emit()` for readdir.
- Namespace filtering uses `struct ns_common::ns_id` instead of raw namespace pointers.

Invariants and risks:
- `kernfs_rwsem` is the central hierarchy mutation lock; many helpers assert it is held read or write.
- Nodes are invisible until active; removal deactivates nodes by adding `KN_DEACTIVATED_BIAS` and waits for active users to drain.
- `kernfs_drain()` temporarily drops hierarchy locks and must pin the target node before doing so.
- Parent pointers and names are RCU-protected; moving across parents also uses `kernfs_rename_lock`.
- `KERNFS_ROOT_INVARIANT_PARENT` forbids cross-parent rename and simplifies path access.
- Self-removal uses `KERNFS_SUICIDAL`/`KERNFS_SUICIDED` to arbitrate concurrent callers and avoid deadlocking on the caller’s own active reference.
- Directory iteration uses hashes as offsets, so hash uniqueness/reserved values and namespace filtering are important for correct traversal.
- Hidden nodes cannot be directories and are deactivated while hidden.
