# File Research: sources/os/bsd/dragonflybsd/sys/vfs/devfs/devfs_core.c

Read completely: 3046 lines.

## Role

This is the core implementation of DragonFlyBSD devfs. It owns global device registration, per-mount devfs topology, devfs node allocation/destruction, alias propagation, clone-handler registration, cdev allocation/reference integration, rule application triggers, devfs message serialization, wildcard matching, and per-file character-device private data.

## Main Responsibilities

- Allocate and free devfs nodes:
  - `devfs_allocp()` creates `Nroot`, `Ndir`, `Nlink`, `Nreg`, or `Ndev` nodes, initializes dirent metadata, permissions, timestamps, parent links, cookies, mount counters, and rules.
  - `devfs_allocv()` maps a devfs node to a DragonFly vnode and attaches character devices through `v_associate_rdev()`.
  - `devfs_freep()` safely tears down vnode association, symlink storage, names, orphan tracking, and final node memory.
  - `devfs_unlinkp()` removes a node from the visible topology and invalidates namecache entries.
- Maintain per-mount topology:
  - `devfs_iterate_topology()` recursively walks the tree.
  - `devfs_gc()` removes nodes, related aliases, and empty generated directories.
  - `devfs_mount_add()` and `devfs_mount_del()` synchronize mount registration/removal with the core thread.
- Maintain global cdev state:
  - `devfs_new_cdev()` allocates and initializes `struct cdev` through `sysref`.
  - `devfs_link_dev()` and `devfs_unlink_dev()` maintain `devfs_dev_list`.
  - `devfs_create_dev()` and `devfs_destroy_dev()` are asynchronous public entry points.
  - `devfs_create_dev_worker()` and `devfs_destroy_dev_worker()` run in the serialized core context.
  - Related-device helpers recursively clear flags or destroy child devices.
- Propagate devices and aliases:
  - `devfs_create_all_dev_worker()` populates a mount with existing devices.
  - `devfs_propagate_dev()` creates or destroys a device node across all devfs mounts.
  - `devfs_make_alias()`, `devfs_destroy_alias()`, and their worker functions maintain `devfs_alias_list`.
  - `devfs_alias_create()` creates `Nlink` nodes pointing at target nodes and increments target link counts.
- Resolve and mutate topology paths:
  - `devfs_resolve_or_create_path()`
  - `devfs_resolve_name_path()`
  - `devfs_create_device_node()`
  - `devfs_destroy_device_node()`
  - `devfs_destroy_node()`
  - `devfs_find_device_node_by_name()`
- Manage clone handlers:
  - `devfs_clone_handler_add()`
  - `devfs_clone_handler_del()`
  - `devfs_clone()` invokes registered clone callbacks outside `devfs_lock`.
- Serialize devfs state through a core message thread:
  - `devfs_msg_core()`
  - `devfs_msg_exec()`
  - `devfs_msg_send()`
  - `devfs_msg_send_sync()`
  - helper send wrappers for names, mounts, ops, handlers, devices, and links.
- Integrate with system facilities:
  - `devfs_config()` waits for pending async devfs work.
  - `devfs_assume_knotes()` takes over device knotes on detach.
  - `devfs_sysctl_devname_helper()` backs `kern.devname` lookup.
  - `devfs_WildCmp()` and `devfs_WildCaseCmp()` implement wildcard matching for rule/name comparisons.
  - `devfs_get_cdevpriv()`, `devfs_set_cdevpriv()`, and `devfs_clear_cdevpriv()` manage per-open file private data.

## Synchronization and Lifetime Model

- `devfs_lock` is the central recursive lock for devfs node, mount, alias, and device-list state.
- `devfs_token` serializes the core message thread.
- Asynchronous public operations post messages to `devfs_msg_port`; synchronous operations wait for replies through `lwkt_domsg()`.
- If a caller is already on the core thread, `devfs_msg_send()` executes directly to avoid self-deadlock.
- Node destruction is interlocked by `DEVFS_DESTROYED`, `DEVFS_NLINKSWAIT`, orphan-list flags, and vnode association checks.
- `devfs_allocv()` and `devfs_freep()` temporarily drop `devfs_lock` around `vget()`/`getnewvnode()`-style vnode operations to avoid deadlocks, then revalidate state.
- `struct cdev` lifetime uses `sysref` plus explicit `reference_dev()`/`release_dev()` references. Device-list membership owns one reference.
- Device-op major IDs are allocated from a clone bitmap and reference-counted in `devfs_dev_ops_list`.

## Important Interactions

- Used by `devfs_vfsops.c` for mount creation, root vnode lookup, mount removal, and file-handle vnode lookup.
- Used by `devfs_vnops.c` for name resolution, vnode allocation, node accessibility checks, cloning, permissions, orphan cleanup, aliases, and cdev private data.
- Used by `devfs_rules.c` for applying hide/show/link/permission rules and resetting rule-created state.
- Sends `udev_event_attach()`/`udev_event_detach()` and `devctl_notify()` events when devices and aliases are created or destroyed.
- Uses VFS helpers such as `v_associate_rdev()`, `v_release_rdev()`, `cache_inval_vp()`, and `vfs_timestamp()`.

## Notable Design Details

- Per-mount devfs trees are regenerated from global `devfs_dev_list` when a mount is added.
- Aliases are implemented as `Nlink` devfs nodes with a `link_target`, not as normal symlink path text unless user-created through vnode operations.
- Lookup of aliases follows up to eight link-target hops to avoid recursion loops.
- PTY devices have special handling: unix98 pty masters and pty-like names can be hidden or invisible until opened.
- Device node names may contain paths; devfs creates intermediate directories on demand.
- `devfs_inode_to_vnode()` walks the topology and allocates a vnode if needed for a matching inode.

## Research Notes

- The highest-risk areas are lock dropping/reacquisition around vnode operations, node destruction while aliases still reference targets, and cdev reference balancing during destroy paths.
- `devfs_destroy_dev_worker()` releases multiple references after unlink and detach; callers must understand which references are owned by device creation, linkage, and the destroy message.
- `devfs_uninit()` sends `DEVFS_TERMINATE_CORE` with a null message even though ordinary send paths expect message storage; this is intentional in context but sensitive to messaging assumptions.
- Wildcard matching allocates temporary backtracking state proportional to the number of `*` wildcards.
