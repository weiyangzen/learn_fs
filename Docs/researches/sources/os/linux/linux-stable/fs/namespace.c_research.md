# File Research: sources/os/linux/linux-stable/fs/namespace.c

## Purpose

`fs/namespace.c` is the Linux VFS mount namespace implementation. It owns mount object lifetime, mount hash lookup, mountpoint tracking, mount namespace allocation and teardown, mount propagation, legacy and modern mount syscalls, `pivot_root()`, `statmount()`, `listmount()`, and namespace operations exposed through proc/nsfs.

This file is central to how Linux represents filesystem topology per mount namespace. It connects VFS objects (`vfsmount`, `mount`, `dentry`, `super_block`) with process namespace state (`mnt_namespace`, `nsproxy`, `fs_struct`) and enforces capability, propagation, idmapped mount, and visibility rules.

## Main Data And Globals

- `sysctl_mount_max`: per-namespace maximum mount count, exposed as `fs.mount-max`.
- `mount_hashtable`: hashes child mounts by `(parent vfsmount, mountpoint dentry)`.
- `mountpoint_hashtable`: hashes `struct mountpoint` by dentry.
- `mnt_cache`: slab cache for `struct mount`.
- `namespace_sem`: global rwsem serializing namespace topology operations.
- `mount_lock`: seqlock protecting mount hash/tree mutations and RCU mount lookup.
- `mnt_id_xa`, `mnt_group_ida`: unique mount ID allocation and peer group IDs.
- `init_mnt_ns`: initial mount namespace.
- `unmounted`, `ex_mountpoints`, `emptied_ns`: deferred cleanup lists protected by `namespace_sem`.

Important internal records:

- `struct mount_kattr`: normalized mount attribute mutation request used by `mount_setattr()` and `open_tree_attr()`.
- `struct pinned_mountpoint`: pins a `struct mountpoint` while a mount operation is being prepared.
- `struct kstatmount`: kernel-side assembly object for `statmount()`.
- `struct klistmount`: kernel-side assembly object for `listmount()`.

## Mount Allocation And Lifetime

Mounts are allocated by `alloc_vfsmnt()`:

- Allocates from `mnt_cache`.
- Allocates old 31-bit mount ID and monotonically increasing unique ID.
- Stores device/source name.
- Allocates per-CPU count/writer counters on SMP.
- Initializes all linkage lists, hash nodes, propagation lists, and default mount idmap.

Mount setup happens in `setup_mnt()`:

- Pins the superblock active count.
- Sets `mnt_sb`, `mnt_root`, parent/self mountpoint defaults.
- Adds the mount to the superblock’s `s_mounts` list.

Lifetime release uses a layered path:

- `mntput()` decrements mount refs.
- `mntput_no_expire()` handles fast path when still namespace-attached.
- `mntput_no_expire_slowpath()` handles final detached cleanup, marks `MNT_DOOMED`, detaches children, schedules task work or delayed work when needed.
- `cleanup_mnt()` verifies writers are gone, kills pins/stuck children, sends fsnotify delete, drops root/superblock, frees ID, then RCU-frees the mount.
- Kernel long-term mounts use `kern_mount()`, `kern_unmount()`, and `kern_unmount_array()`.

The file relies heavily on RCU and seqlock retry patterns so path walking can safely observe mounts while topology changes.

## Mount Lookup And Mountpoints

`__lookup_mnt()` is the low-level hash lookup for a child mounted at a parent/dentry pair. `lookup_mnt()` wraps it with RCU and `legitimize_mnt()` to return a referenced `vfsmount`.

Mountpoint objects are managed by:

- `get_mountpoint()`: finds or creates a `struct mountpoint` for a dentry, sets `DCACHE_MOUNTED`, and pins it in a caller-provided `pinned_mountpoint`.
- `lookup_mountpoint()`: hash lookup and pin insertion.
- `unpin_mountpoint()`: removes the pin and possibly frees the mountpoint.
- `maybe_free_mountpoint()`: clears `DCACHE_MOUNTED`, drops dentry, removes from hash when no mounts/pins remain.

`path_is_mountpoint()` checks whether a specific path is a mountpoint in the current namespace, while `__is_local_mountpoint()` checks by dentry across the current namespace.

## Write Access And Read-Only Transitions

The file maintains per-mount writer counters to make remount-readonly safe:

- `mnt_get_write_access()` increments writer count, waits out `WRITE_HOLD`, then checks read-only state.
- `mnt_want_write()` also takes superblock freeze protection.
- `mnt_get_write_access_file()` and `mnt_want_write_file()` optimize for files already opened for write.
- `mnt_put_write_access()` / `mnt_drop_write()` release.
- `mnt_hold_writers()` sets `WRITE_HOLD` and verifies no active writers.
- `mnt_unhold_writers()` releases the hold after publishing read-only flag changes.
- `sb_prepare_remount_readonly()` walks all mounts of a superblock and holds writers before transitioning the superblock read-only.

The memory barriers around writer counters, `WRITE_HOLD`, and `s_readonly_remount` are core correctness points.

## Attaching, Detaching, And Tree Topology

Core topology helpers:

- `mnt_set_mountpoint()`: sets parent/mountpoint/mp linkage.
- `make_visible()`: adds a mount to hash and parent child list; also records overmount relationships.
- `attach_mnt()`: combines mountpoint setup and visibility.
- `mnt_change_mountpoint()`: moves an existing mount to a different parent/mountpoint.
- `mnt_add_to_ns()`: inserts mount into namespace RB tree ordered by unique ID and queues notification.
- `commit_tree()`: attaches a tree to a namespace and publishes it.
- `next_mnt()` / `skip_mnt_tree()`: depth-first mount tree traversal.

Unmounting is handled by:

- `umount_tree()`: gathers a subtree, handles propagation, removes mounts from namespaces, optionally disconnects, and queues references for cleanup.
- `do_umount()`: implements policy for `umount(2)`, including expire, force, detach, busy checks, locked mounts, root remount-readonly special case.
- `path_umount()` and `ksys_umount()` are syscall helpers.
- `__detach_mounts()` lazily detaches mounts from a dentry during unlink/drop-style paths.
- `mark_mounts_for_expiry()` and `shrink_submounts()` expire shrinkable/unused mounts.

`namespace_unlock()` performs deferred cleanup and fsnotify delivery after topology operations, downgrading locks when possible for notifications.

## Mount Propagation And Copying

Propagation logic is integrated with `pnode.c` helpers:

- `clone_mnt()` clones a mount, preserving or altering peer/slave/private state based on flags.
- `copy_tree()` recursively clones a subtree, respecting unbindable mounts, locked mounts, and namespace-file loop prevention.
- `invent_group_ids()` allocates peer group IDs for making mounts shared.
- `cleanup_group_ids()` rolls group IDs back after failures.
- `attach_recursive_mnt()` attaches or moves a mount tree and handles propagation into peer groups, locking across user namespace boundaries, pending mount counts, overmount handoff, and failure cleanup.
- `do_change_type()` changes mount propagation type for one mount or recursively.
- `do_set_group()` sets sharing/slave group relationship between two mount roots.

The file is careful to reject propagation cases that would create loops or meaningless overmounts, especially in `can_move_mount_beneath()` and `check_for_nsfs_mounts()`.

## Legacy Mount API

Legacy `mount(2)` flow:

- `SYSCALL_DEFINE5(mount)` copies type/source/options from userspace.
- `do_mount()` resolves target path.
- `path_mount()` parses flags into superblock flags and mount flags, checks LSM and capabilities, warns for deprecated `mand`, then dispatches:
  - `MS_REMOUNT|MS_BIND` -> `do_reconfigure_mnt()`
  - `MS_REMOUNT` -> `do_remount()`
  - `MS_BIND` -> `do_loopback()`
  - propagation flags -> `do_change_type()`
  - `MS_MOVE` -> `do_move_mount_old()`
  - otherwise -> `do_new_mount()`
- `do_new_mount()` gets filesystem type, creates an `fs_context`, parses source/options, checks mount capability, and delegates to `do_new_mount_fc()`.
- `do_new_mount_fc()` gets the tree, runs LSM mount checks, rejects overly revealing mounts, warns about timestamp expiry, locks the mountpoint, and attaches.

`copy_mount_options()` and `copy_mount_string()` handle legacy userspace data copying.

## Modern Mount API

Modern syscalls implemented here:

- `open_tree()`: opens a path as an O_PATH file, clones a tree into an anonymous namespace, or creates a new mount namespace with `OPEN_TREE_NAMESPACE`.
- `open_tree_attr()`: variant that can apply mount attributes before publishing the fd.
- `fsmount()`: converts an `fsopen()` context with a prepared root into a detached mount fd, or a namespace file with `FSMOUNT_NAMESPACE`.
- `move_mount()`: moves a mount tree, installs detached mounts, handles fd/path targets, supports `MOVE_MOUNT_BENEATH`, and supports propagation-group setting.
- `mount_setattr()`: changes mount attributes, propagation, and idmapping recursively or non-recursively.

Important validation:

- `can_change_locked_flags()` prevents clearing locked read-only, nodev, nosuid, noexec, or atime restrictions.
- `can_idmap_mount()` restricts idmapped mounts to anonymous, not-yet-exposed mounts, supported filesystems, controlled superblocks, and non-filesystem-wide idmaps.
- `build_mount_kattr()` normalizes userspace `struct mount_attr`.
- `mount_setattr_prepare()` holds writers where needed before commit.
- `mount_setattr_commit()` updates idmaps, flags, propagation, and namespace event.

## Namespace Creation And Switching

Mount namespaces are allocated by `alloc_mnt_ns()`:

- Charges user namespace ucounts.
- Initializes namespace ID, passive refcount, RB tree, poll waitqueue, user namespace ref, and anonymous flag.

Namespace copy and creation:

- `copy_mnt_ns()` implements `CLONE_NEWNS`, including empty mount namespace support and user namespace crossing behavior.
- `create_new_namespace()` builds a new namespace for `OPEN_TREE_NAMESPACE`/`FSMOUNT_NAMESPACE`.
- `get_detached_copy()` creates anonymous detached namespace copies for cloned mount-tree file descriptors.
- `mount_subtree()` mounts and looks up a subtree in an anonymous namespace.

Namespace lifetime:

- `put_mnt_ns()` drops active refs and tears down the root tree when the namespace is no longer active.
- `mnt_ns_release()` frees passive refs after RCU.
- `lookup_mnt_ns()` finds namespaces by ID for `statmount()`/`listmount()`.

Proc namespace ops:

- `mntns_get()`, `mntns_put()`, `mntns_install()`, `mntns_owner()`.
- `mntns_install()` requires capability over both target and caller user namespaces, rejects anonymous namespaces, and updates root/pwd.

## Root And Path Operations

`pivot_root()` is implemented by:

- `SYSCALL_DEFINE2(pivot_root)` resolving `new_root` and `put_old`.
- `path_pivot_root()` enforcing mountpoint, reachability, shared propagation, lock, and namespace constraints.
- It reattaches `new_root` over old root and old root under `put_old`, then updates fs refs with `chroot_fs_refs()`.

Path reachability helpers:

- `is_path_reachable()` tests whether a mount/dentry is reachable from a root.
- `path_is_under()` exports this check under the mount seqlock.
- `current_chrooted()` tests whether the current fs root differs from namespace root.

## statmount() And listmount()

This file implements newer mount inspection syscalls.

`statmount()`:

- Parses `struct mnt_id_req`.
- Can identify target by mount namespace + unique mount ID, namespace fd, or mount fd (`STATMOUNT_BY_FD`).
- Assembles fixed fields and variable strings/options into `struct statmount`.
- Supports superblock basics, mount basics, propagation info, root, mount point, fs type/subtype, source, option strings/arrays, security options, namespace ID, and idmap uid/gid maps.
- Retries with larger seq buffer on `-EAGAIN`.

`listmount()`:

- Lists unique mount IDs under a parent ID or namespace root.
- Supports reverse order.
- Uses namespace RB tree ordering and reachability checks.
- Enforces capability behavior for inaccessible namespace views.

These syscalls rely on `namespace_sem` read locking for topology stability but intentionally tolerate concurrent mount flag/idmap changes using `READ_ONCE()`/`WRITE_ONCE()` semantics.

## Security And Namespace Policy

Security/capability checks appear throughout:

- `may_mount()` requires `CAP_SYS_ADMIN` in the current mount namespace owner user namespace.
- LSM hooks: `security_sb_mount`, `security_sb_umount`, `security_sb_kern_mount`, `security_move_mount`, `security_sb_pivotroot`, `security_sb_statfs`, `security_sb_show_options`.
- `mount_too_revealing()` prevents exposing userns-visible special filesystems too permissively unless already visible with safe locked attributes.
- `mnt_may_suid()` rejects suid trust on foreign mounts and requires current user namespace compatibility.
- Locked mount flags prevent less-privileged namespaces from relaxing inherited constraints.
- Namespace-file bind loops are rejected through `mnt_ns_loop()` and `check_for_nsfs_mounts()`.

## Initialization

`mnt_init()`:

- Creates `mnt_cache`.
- Allocates mount and mountpoint hash tables.
- Initializes kernfs, sysfs, `/sys/fs`, shmem, rootfs.
- Calls `init_mount_tree()`.

`init_mount_tree()`:

- Creates immutable `nullfs` mount as namespace root.
- Mounts mutable `rootfs` over it.
- Adds both mounts to `init_mnt_ns`.
- Sets init task root and cwd to mutable rootfs.
- Adds initial namespace to namespace tree.

## Error Handling And Failure Paths

The file uses rollback-oriented patterns:

- Failed mount attachment unmounts cloned trees with `umount_tree()`.
- Failed propagation cleans pending counts and group IDs.
- Failed namespace creation stores `emptied_ns` for cleanup on `namespace_unlock()`.
- `__free` cleanup annotations are used for paths, mounts, namespaces, files, and ID maps.
- Mount operations carefully avoid dropping final refs under locks unless topology guarantees stability.

## Key Takeaways

`namespace.c` is the mount topology authority for Linux. It combines high-concurrency lookup, serialized topology mutation, propagation semantics, namespace ownership, idmapped mount policy, and syscall-facing mount management. Correctness depends on the interaction between `namespace_sem`, `mount_lock`, RCU, mount refcounts, writer holds, namespace passive refs, and explicit failure rollback.
