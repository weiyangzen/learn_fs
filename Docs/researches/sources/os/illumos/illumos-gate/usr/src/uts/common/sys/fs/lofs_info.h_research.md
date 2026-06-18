# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/lofs_info.h

This header defines loopback filesystem per-mount and hash-table state.

Hashing:
- `lobucket` holds a per-bucket lock, lnode chain, vnode count, and padding to avoid false sharing.
- `lo_retired_ht` tracks retired hash tables for deferred cleanup.

Mount state:
- `loinfo` stores real VFS, loopback VFS, root vnode, inherited and denied mount flags, outstanding vnode count, volatile hashtable size/table pointer, list of loopback VFS mappings, locks for that list and hash table/retired state, and filesystem behavior flags.
- Inheritable mount flags include readonly, nosetuid, nodevices, xattr, nbmand, and noexec.

Mount options/flags:
- `MNTOPT_LOFS_NOSUB` and `MNTOPT_LOFS_SUB` control submount traversal.
- `LO_NOSUB` provides NFS-server-like lookup semantics where mountpoints are not traversed.

Cross-VFS mapping:
- `lfsnode` records a real VFS/root and a new loopback VFS for real filesystems encountered during loopback namespace traversal.

Conversion:
- `vtoli()` maps VFS to `loinfo`.

Kernel API:
- Functions for resolving real VFS, subsystem init/fini, hashtable setup/destroy, and vnode/vfs operation globals.

Dependencies and relationships:
- Paired with `lofs_node.h`, which defines individual lnodes.
- Handles loopback views that may cross underlying VFS boundaries.
