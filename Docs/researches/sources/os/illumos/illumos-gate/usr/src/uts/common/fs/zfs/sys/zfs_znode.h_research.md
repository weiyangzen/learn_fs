# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_znode.h

Defines per-file znode state, persistent file flags, SA attribute lookup macros, directory-entry locks, vnode/ZFS entry macros, timestamp helpers, and ZIL logging entry points for ZPL operations.

Key elements:
- Persistent pflags include readonly, hidden, system, archive, immutable, nounlink, append-only, nodump, opaque, antivirus, reparse, offline, sparse, project inheritance, and project ID.
- Internal flags include xattr, inheritable ACE, trivial ACL, object ACE, protected/defaulted/autoinherit ACL, scanstamp, and exec-deny state.
- SA macros map ZPL attributes through `zfsvfs_t->z_attr_table`.
- `zfs_dirlock_t` serializes per-directory name operations.
- `znode_t` stores filesystem/vnode pointers, object ID, locks, range lock, cached metadata, ACL cache, project ID, all-znode list linkage, SA handle, and native-SA flag.
- `ZFS_ENTER`, `ZFS_EXIT`, and `ZFS_VERIFY_ZP` guard vnode/vfs operation entry against teardown/unmount.

Main dependencies and interactions:
- Kernel includes VFS/ZPL state, SA, stats, rrwlock, and range locks.
- Declares core functions for filesystem init/create, zget/rezget/inactive/delete/free, sync, object-to-path/stats, timestamp update, freespace, block growth, upgrades, share dir creation, and page map/unmap.
- Declares ZIL log helpers for create/remove/link/symlink/rename/write/truncate/setattr/ACL.

Implementation notes:
- The range-lock rules are documented here and govern file size/read/write/truncate correctness.
- Project ID inheritance is inline: child objects inherit only when parent has `ZFS_PROJINHERIT`.
