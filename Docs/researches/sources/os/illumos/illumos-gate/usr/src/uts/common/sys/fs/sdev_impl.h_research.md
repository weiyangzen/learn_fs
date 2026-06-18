# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/sdev_impl.h

This private header defines the implementation state for the `/dev` filesystem (`sdev`), including dynamic device nodes, profiles, plugin support, devfsadm communication, negative caching, vnode operation selection, and debug support.

Mount/profile ABI:
- `sdev_mountargs` currently carries `sdev_attrdir`.
- Profile nvpair names cover mount point, include, exclude, symlink, and map entries.
- `sdev_door_arg_t` and `sdev_door_res_t` define devfsadm/devname door command/result payloads.
- Supported devfsadm command is run-all; errors include invalid, EPERM, and not supported.

Profile and instance data:
- `sdev_dprof` stores profile nvlists for names, maps, symlinks, and glob include/exclude directories.
- `devname_handle` binds a handle to an `sdev_node` plus callback arguments.
- Global-zone instance data stores a handle and namespace generation.
- Local-zone data stores cached directory/devtree generations, origin global node, and profile.

Node model:
- `sdev_node_t` stores name, length, absolute path, symlink target, vnode, contents rwlock, parent, AVL directory entries/link, backing attribute vnode, in-memory attributes, inode, link count, state, flags, lookup synchronization lock/cv/flags, per-instance global/local union, plugin-list link, and private pointer.
- Node states are zombie, init, and ready.
- Directory traversal macros wrap AVL first/next.
- Conversion/hold/release macros bridge vnode and sdev_node.

Flags:
- Node flags include build/out-of-date, global, persisted, no negative cache, dynamic vnode ops, validate during search, invalid attributes, subdir match, and zoned subdir.
- Lookup flags include lookup in progress, readdir in progress, and waiting for devfsadm.
- Default uid/gid/modes are defined for root, directories, devices, and symlinks.

Filesystem instance:
- `sdev_data` stores mount list links, root node, VFS pointer, mount args, and ACL flavor.
- `sdev_fid` overlays VFS fid with length, inode, and generation.

Synchronization/devfsadm:
- Macros manage devfsadm state: stopped, running, ran once.
- `SDEV_BLOCK_OTHERS`, `SDEV_UNBLOCK_OTHERS`, and lookup-wait helpers coordinate concurrent lookup/readdir/devfsadm actions.
- Boot states progress through initial, reconfig, system available, and complete.

Negative cache:
- `sdev_nc_list_t` stores list, mutex, rwlock, flags, and entry count.
- `sdev_nc_node_t` stores missing-name entries, source flags, expiration count, and list linkage.
- Flags identify dirty/writing/write-enabled lists and active/persistent/current-boot entries.
- Devname-cache nvlist identifiers define persistent cache format.

Vnode/plugin helpers:
- Declares generic lookup/readdir/setattr/inactive helper functions, cache lookup/update, root/node construction, dynamic filldir, node ready/destroy/update, shadowing, stale/cleandir/rename, attribute/default helpers, backstore lookup, profile functions, validators for devpts/devnet/devipnet/devvt/devzvol, and devinfo/modctl helpers.
- `sdev_vop_table_t` maps subdirectory names to vnode ops templates, global vnode-op containers, validators, and flags.
- Plugin lifecycle and node-ready hooks integrate with `sdev_plugin.h`.

Globals:
- Exposes locks, devtype, node cache, vnode ops for base and special subtrees, mount origins, operation tables, negative cache pointer, reconfig and negative-cache tunables, and taskq.

Debugging:
- DEBUG builds expose many per-subsystem debug flags and conditional trace macros, including failed lookup tracing.

Dependencies and relationships:
- This is the main implementation contract for `/dev` dynamic filesystem internals.
- It is used by devfs/sdev vnode operations, devfsadm integration, non-global zone `/dev` profiles, plugin modules, and special dynamic subdirectories.
