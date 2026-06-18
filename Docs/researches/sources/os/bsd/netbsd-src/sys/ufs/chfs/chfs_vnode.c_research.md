# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_vnode.c

Purpose: Implements vnode/inode construction helpers, on-flash vnode/dirent loading, inode creation, vnode size updates, and per-eraseblock size accounting helpers.

Key entry points:
- `chfs_vnode_lookup`: finds an active vnode by inode number using NetBSD vnode iterator.
- `chfs_readvnode`: reads a flash vnode metadata node into an existing inode/vnode.
- `chfs_readdirent`: reads one flash dirent node and adds it to a parent inode.
- `chfs_makeinode`: creates a new inode/vnode, writes vnode metadata, updates parent, writes dirent.
- `chfs_set_vnode_size`: synchronizes inode and vnode size fields.
- `chfs_change_size_free/dirty/unchecked/used/wasted`: shared mount/block accounting helpers.

Important behavior:
- New inodes allocate a new vnode number from `chm_max_vno`, create/update vnode-cache state, initialize metadata, write both child and parent vnode nodes, then write a parent dirent.
- Directories start with size 512 and link count 2; non-directories start size 0 and link count 1.
- Flash vnode read skips root because root is in-memory only.
- Size helpers assert accounting never becomes negative or exceeds eraseblock size.

Dependencies:
- Uses write helpers from `chfs_write.c`, dirent insertion from `chfs_nodeops.c`, vnode-cache hash, and NetBSD kauth/genfs.

Research notes:
- Parent `nlink` is incremented after every `chfs_makeinode`, including non-directory creation, which is notable compared with traditional directory link semantics.
- Some error paths after partial flash writes rely on callers or later GC/replay to clean up.
