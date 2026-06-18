# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/namenode.h

This header defines NAMEFS structures for mounting file descriptors into the filesystem namespace.

User/kernel ABI:
- `struct namefd` carries a file descriptor from userland to kernel for `fattach()`/NAMEFS use.

Kernel node model:
- `namenode` stores the mounted-file-descriptor vnode, flags, copied attributes, original file vnode, file pointer, original mountpoint vnode, list linkage, and a lock protecting attributes.
- `NMNMNT` indicates a namenode is not mounted.

Hashing:
- `NM_FILEVP_HASH_SIZE` is 64.
- `NM_FILEVP_HASH(vp)` hashes by shifted vnode pointer into `nm_filevp_hash`.

Conversions:
- `VTONM` maps vnode to namenode.
- `NMTOV` maps namenode to vnode.

Kernel API:
- Initialization, unmount-all, insert/remove/find, node number allocation/free, vnode ops/template, table lock.
- `nm_walk_mounts()` walks NAMEFS mounts for a vnode with a callback.

Dependencies and relationships:
- NAMEFS is used by `fattach()` to bind an open file descriptor into a path.
- Stores both the mounted file vnode and the mountpoint vnode to support lookup/unmount behavior.
