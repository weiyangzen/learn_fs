# File Research: sources/teaching/os161/kern/fs/sfs/sfs_inode.c

Implements SFS inode/vnode lifecycle.

Key functions:
- `sfs_sync_inode` writes dirty in-memory inode state (`sv_i`) to disk block `sv_ino`.
- `sfs_reclaim` handles vnode final release: rechecks refcount, truncates data if link count is zero, syncs the inode, frees the inode block when unlinked, removes the vnode from `sfs_vnodes`, cleans up generic vnode state, and frees memory.
- `sfs_loadvnode` first searches the resident vnode table, increments refcount if found, otherwise allocates an `sfs_vnode`, verifies the inode block is allocated, reads the dinode, optionally forces a type for newly created objects, selects file or directory vnode ops, initializes the generic vnode, and inserts it into the resident table.
- `sfs_makeobj` allocates an inode block and loads it as a new vnode of the requested type.
- `sfs_getroot` loads inode `SFS_ROOTDIR_INO` and verifies it is a directory.

Notable invariants:
- Inode number equals the disk block number containing the dinode.
- Every loaded inode must be marked allocated in the freemap.
- Linkcount zero plus no vnode refs triggers data and inode reclamation.
