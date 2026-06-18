# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_subr.c

This file provides the shared implementation for the illumos `/dev` filesystem: node allocation, attribute handling, directory cache operations, lookup/readdir algorithms, persistent backing-store integration, rename/cleanup, modctl helper operations, generic setattr, and inactive teardown.

Major exported/default state:
- Prototype vattrs for directory, symlink, block, and character nodes.
- `sdev_node_cache`.
- `devtype`.
- Legacy dynamic directory table `vtab` for `pts`, `vt`, `zvol`, `zcons`, `net`, `ipnet`, `lofi`, and `rlofi`.

Node lifecycle:
- `sdev_node_cache_init()` and `sdev_node_cache_fini()` manage the kmem cache.
- `sdev_nodeinit()` allocates an `sdev_node`, names/path it, initializes vnode state, inherits flags, and sets initial state.
- `sdev_nodeready()` transitions a node to `SDEV_READY`, initializes directory AVL state, symlink target, plugin state, non-global origin, attributes, and optional persistent shadow vnode.
- `sdev_mkroot()` builds the filesystem root node and marks global `/dev` roots as global/persistent.
- `sdev_nodedestroy()` releases backing vnode, attributes, names, symlink target, profile nvlists, origins, AVL state, locks, and returns the node to the cache.
- `devname_inactive_func()` handles vnode inactive callbacks, destroying zombie nodes only when the final reference drops.

Directory cache and mutation:
- `sdev_findbyname()`, `sdev_direnter()`, `sdev_dirdelete()`, `sdev_cache_update()`, and `sdev_cache_lookup()` implement the in-core AVL directory cache.
- `sdev_stale()` recursively marks cached children stale/zombie and sets rebuild state.
- `sdev_cleandir()` recursively removes children, optionally enforcing deletion of busy nodes, and cleans persistent backing-store entries.
- `sdev_rnmnode()` implements rename by validating hierarchy constraints, handling symlink targets, replacing existing destinations, recursively moving directory contents, creating a fresh destination node, and updating timestamps.

Lookup and directory fill:
- `devname_lookup_func()` is the central lookup path. It checks `.`, `..`, cache entries, backing store, dynamic callbacks, implicit devfsadm reconfiguration, negative cache filtering, validators, stale recreation, and spec vnode conversion.
- `sdev_call_dircallback()` creates dynamic symlink or vattr-based nodes from directory-specific callbacks.
- `sdev_call_devfsadmd()` coordinates implicit reconfiguration through devfsadmd.
- `sdev_filldir_from_store()` populates cache entries from the persistent backing directory.
- `sdev_filldir_dynamic()` pre-creates dynamic legacy directories under global `/dev`.
- `devname_readdir_func()` is the common readdir formatter; it optionally triggers devfsadm for browse reads, waits for rebuilds, fills from backing store, emits `.`, `..`, and ready cached entries, and applies validators.
- `add_dir_entry()` is a small dirent construction helper.

Persistence and attributes:
- `sdev_shadow_node()` creates or finds a persistent backing-store vnode for a node.
- `devname_backstore_lookup()` wraps lookup in the backing store.
- `sdev_vattr_merge()` overlays sdev inode/link/type/rdev information onto vattrs.
- `sdev_getdefault_attr()` returns default vattr templates.
- `sdev_update_timestamps()` writes timestamp changes to a vnode.
- `devname_setattr_func()` implements common setattr logic, using backing-store setattr when available, creating a shadow node for persistent or non-dynamic metadata changes, or updating in-memory attributes with policy checks.

Modctl helpers:
- `sdev_modctl_lookup()` resolves a path through global root, follows symlinks and mountpoints, and returns only the persisted vnode underlying `/dev`.
- `sdev_modctl_readdir()` lists persisted directory contents for module-control callers.
- `sdev_modctl_readdir_free()` frees returned lists.
- `sdev_modctl_devexists()` checks whether a persisted device path exists.

Important dependencies include VFS/vnode operations, specfs `specvp()`, AVL trees, sdev plugin hooks, devfsadm communication, negative cache helpers, backing-store filesystem VOPs, PTMS/net/ipnet validators through `vtab`, and zone/profile state.

Risk areas:
- Locking is complex: parent directory contents locks, child contents locks, vnode locks, lookup locks, and backing-store VOP calls interact across many paths.
- `SDEV_INIT`, `SDEV_READY`, and `SDEV_ZOMBIE` transitions are central to avoiding duplicate construction and dangling visible nodes.
- Persistent backing-store cleanup errors are intentionally logged but often not propagated.
- `devname_lookup_func()` has many early exits; reference release and negative-cache updates must stay balanced.
