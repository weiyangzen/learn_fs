# File Research: sources/os/linux/linux/fs/namespace.c

## Role

Core Linux VFS mount namespace implementation. This file owns `struct mount` allocation/lifetime, mount hash and mountpoint hash management, mount namespace allocation/destruction, mount tree cloning and movement, propagation semantics, mount write access accounting, legacy and new mount API syscalls, idmapped mount attribute changes, mount namespace introspection, root mount initialization, and mount namespace `proc_ns_operations`.

## Core State and Locking

- `sysctl_mount_max` limits mounts per namespace and is exposed as `fs.mount-max` when sysctl is enabled.
- Global hash tables index child mounts by `(parent vfsmount, mountpoint dentry)` and mountpoints by dentry.
- `namespace_sem` serializes topology changes, namespace teardown, proc/list/stat mount iteration, and deferred mountpoint cleanup.
- `mount_lock` is a seqlock protecting mount tree/hash mutation and lockless path-walk validation.
- Mount IDs use both an xarray-backed legacy 31-bit `mnt_id` and a monotonically increasing `mnt_id_unique`, with `MNT_UNIQUE_ID_OFFSET` avoiding confusion with old IDs.
- Mount namespaces are tracked in the namespace tree, have active and passive references, rb-tree indexed mounts, first/last rb nodes for iteration, poll event counters, owner user namespace, and ucount accounting.
- `struct pinned_mountpoint` temporarily links a caller to a `struct mountpoint` while attaching or moving mounts, preventing the mountpoint from disappearing.

## Mount Lifetime and Write Access

- `alloc_vfsmnt()` allocates a mount, assigns IDs, initializes per-CPU mount counts/writer counts, list/hash nodes, and default `nop_mnt_idmap`.
- `setup_mnt()` binds a configured superblock root to a new mount and registers it on the superblock mount list.
- `mntget()` and `mntput()` implement mount reference counting with RCU-aware finalization. Cleanup removes IDs, fsnotify state, dentries, superblock activity, stuck children, and delayed frees.
- `mnt_make_shortterm()`, `kern_mount()`, `kern_unmount()`, and `kern_unmount_array()` support long-lived internal kernel mounts.
- `mnt_get_write_access()`, `mnt_want_write()`, file variants, and matching drop/put helpers protect read-only transitions and freezer state.
- `mnt_hold_writers()` and `mnt_unhold_writers()` set `WRITE_HOLD` while summing per-CPU writer counts so read-only remounts and mount attribute changes can safely block new writers.
- `sb_prepare_remount_readonly()` applies writer holds across every mount of a superblock before beginning the superblock read-only state transition.

## Mount Lookup and Mountpoints

- `__lookup_mnt()` and `lookup_mnt()` locate a child mount at a path, using `mount_lock` sequence validation and `__legitimize_mnt()` to safely take references under RCU.
- `path_is_mountpoint()` and `__is_local_mountpoint()` distinguish local namespace mountpoints from dentries mounted elsewhere.
- `get_mountpoint()` either pins an existing mountpoint or allocates a new one, sets `DCACHE_MOUNTED`, hashes it, and attaches a pin.
- `maybe_free_mountpoint()` clears `DCACHE_MOUNTED`, unhashes, queues dentry shrinking, and frees the mountpoint when no mounts or pins remain.
- `mnt_set_mountpoint()`, `make_visible()`, `attach_mnt()`, and `mnt_change_mountpoint()` attach or reparent mounts into visible parent/child and hash structures.

## Namespace Tree and Propagation

- `mnt_add_to_ns()` inserts mounts into a namespace rb-tree by unique ID and tracks first/last nodes plus visibility for restricted user-namespace mounts.
- `next_mnt()` and `skip_mnt_tree()` traverse mount subtrees in depth-first order.
- `commit_tree()` attaches newly added mount trees to the parent namespace, increments mount counts, makes the root visible, and notifies waiters.
- `clone_mnt()` duplicates a mount, preserving or adjusting mount flags, peer group, slave/master relationships, idmap, and expiry membership depending on clone flags.
- `copy_tree()` recursively clones eligible submounts, skipping or rejecting unbindable and mount-namespace-file mounts depending on flags.
- `attach_recursive_mnt()` implements the core bind/move attach path: counts mounts, propagates into shared peers, allocates group IDs, handles anonymous namespace source trees, reattaches moved mounts, commits all propagated copies, and transfers locked overmount responsibility where needed.
- Propagation mode changes are handled by `do_change_type()`, `invent_group_ids()`, `cleanup_group_ids()`, and `change_mnt_propagation()` from propagation helpers.
- `do_set_group()` supports `MOVE_MOUNT_SET_GROUP`, allowing a private mount to inherit sharing/slave relationships from a wider mount on the same superblock under strict ancestry and locked-child checks.

## Unmount and Expiry

- `may_umount_tree()` and `may_umount()` check whether mount trees appear busy.
- `umount_tree()` detaches a tree, optionally propagates unmounts, makes mounts private, updates namespace counts/events, handles connected lazy unmounts, queues fsnotify, and defers final `mntput()`.
- `do_umount()` implements regular, lazy, forced, and expiry unmount behavior, including special root handling via read-only remount.
- `__detach_mounts()` lazily disconnects all mounts on a dentry being unlinked/dropped.
- `mnt_set_expiry()`, `mark_mounts_for_expiry()`, `select_submounts()`, and `shrink_submounts()` support automount expiry and shrinkable submount cleanup.

## Mount Creation and Legacy API

- `vfs_create_mount()`, `fc_mount()`, `fc_mount_longterm()`, and `vfs_kern_mount()` convert prepared `fs_context` objects or filesystem types into detached mounts.
- `do_new_mount()` implements legacy mount creation: resolves filesystem type/subtype, creates `fs_context`, parses source/options, checks capabilities, and attaches via `do_new_mount_fc()`.
- `path_mount()` decodes legacy `mount(2)` flags into superblock flags and per-mount flags, warns on deprecated mandatory locking, and dispatches remount, bind, propagation, move, or new mount operations.
- `SYSCALL_DEFINE5(mount)` copies user strings/options and calls `do_mount()`.
- `do_reconfigure_mnt()` handles `MS_REMOUNT|MS_BIND`, changing only per-mount flags.
- `do_remount()` reconfigures the underlying superblock through `fs_context_for_reconfigure()` and then updates mount attributes.
- Timestamp expiry warnings are emitted for writable mounts whose filesystem timestamp maximum is within the uptime horizon.

## New Mount API

- `open_tree()` can return an `O_PATH` reference, a detached clone, or a new mount namespace containing a cloned tree.
- `fsmount()` turns a configured `fs_context` fd into either an anonymous detached mount fd or a new namespace fd, applying mount attributes and “too revealing” checks first.
- `move_mount()` moves or attaches mount trees from path or fd sources to path or fd targets, with support for beneath-mount semantics and propagation group setup.
- `mount_setattr()` changes mount attributes recursively or singly, including read-only, nosuid/nodev/noexec, atime policy, nosymfollow, propagation, and idmapped mount state.
- `open_tree_attr()` combines `open_tree()` with optional attribute changes before publishing the fd.
- `can_idmap_mount()` restricts idmapped mounts to filesystems that opt in, non-initial user namespaces, mounts not yet visible outside anonymous namespaces, and callers capable in relevant namespaces.
- `mount_setattr_prepare()` validates locked flags and idmap eligibility and holds writers when needed; `mount_setattr_commit()` swaps idmaps, writes flags, releases holds, and changes propagation.

## Root, Namespace Copying, and Pivot

- `alloc_mnt_ns()` creates regular or anonymous mount namespaces, initializes namespace IDs, ucounts, rb-tree state, poll waitqueue, passive refs, and user namespace ownership.
- `copy_mnt_ns()` implements `CLONE_NEWNS`, including empty mount namespaces, recursive tree copy, cross-user-namespace slave conversion, locked mount trees, and root/pwd remapping.
- `mount_subtree()` temporarily places a mount in an anonymous namespace to resolve and return a subtree root with an active superblock reference.
- `init_mount_tree()` creates an immutable `nullfs` mount and mutable `rootfs` overmount, installs them into `init_mnt_ns`, sets init task root/pwd to rootfs, and registers the namespace.
- `mnt_init()` creates caches/hash tables, initializes kernfs/sysfs/shmem/rootfs, creates `/sys/fs`, and calls `init_mount_tree()`.
- `path_pivot_root()` and `pivot_root()` enforce non-shared, mounted, reachable roots, then atomically swap the root mount and old root mount and update process fs references.

## Introspection and Proc Namespace Operations

- `/proc` mount iteration uses `mounts_op`, reading namespace mounts in unique-ID order under `namespace_sem`.
- `statmount()` fills `struct statmount` fields selected by a mask: superblock basics, mount IDs, old IDs, attributes, propagation, peer/master IDs, root path, mountpoint, type/subtype, source, options, security options, mount namespace ID, supported mask, and idmap uid/gid maps.
- `listmount()` returns mount IDs below a parent or namespace root, forward or reverse, filtering by reachability and permission.
- `lookup_mnt_ns()`, `grab_requested_mnt_ns()`, and fd/ns-id handling allow introspection of another mount namespace with passive references and capability checks.
- `mntns_operations` implements proc namespace get/put/install/owner. Installing a mount namespace requires capability in both target and caller user namespaces, rejects anonymous namespaces, requires a private `fs_struct`, switches namespace, and resets root/pwd.

## Security and User Namespace Constraints

- `may_mount()` gates namespace mutation on `CAP_SYS_ADMIN` in the current mount namespace owner.
- LSM hooks are called for mount, unmount, move mount, pivot root, kernel mount, and statfs-style disclosure.
- Locked mount flags prevent less privileged namespaces from clearing readonly, nodev, nosuid, noexec, or atime restrictions.
- `lock_mnt_tree()` locks sensitive attributes when a tree crosses user namespace boundaries and hides covered mounts from unprivileged exposure.
- `mount_too_revealing()` prevents restricted pseudo-filesystems from exposing a fuller view inside non-initial user namespaces unless an adequate visible mount already exists.
- `mnt_may_suid()` treats foreign mounts as nosuid and requires the current user namespace to match the superblock user namespace.

## Dependencies

Uses VFS internals, fs contexts, path lookup, dcache/mount propagation helpers, fsnotify, LSM hooks, user namespaces, namespace tree APIs, xarray/IDA, sysctl, proc namespace APIs, idmapped mount helpers, rootfs/nullfs/shmem initialization, and architecture syscall glue.

## Research Notes

This file is the central mount topology authority in Linux. Its main invariants are lock ordering, mount visibility under RCU path walk, propagation correctness, namespace ownership/capability checks, and writer exclusion during read-only/idmap transitions. The newer fd-based mount API and `statmount()`/`listmount()` code coexist with legacy `mount(2)` and `umount(2)` while sharing the same core tree, propagation, and lifetime machinery.
