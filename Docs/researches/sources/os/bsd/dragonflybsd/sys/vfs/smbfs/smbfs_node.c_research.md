# File Research: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/smbfs_node.c

This file manages SMBFS vnode-private nodes, name storage, vnode lookup hashing, reclaim/inactive handling, and attribute caching.

It defines the FNV-style `smbfs_hash` used for name hashing and the per-mount vnode hash table lookup. `smbfs_node_alloc` is the central allocator/lookup routine: it handles special `..` lookup, rejects `.`, searches the hash table for an existing `(parent, name)` node, safely retries after `vget`, and creates a new vnode/smbnode pair when attributes are supplied.

New nodes receive type from SMB DOS attributes, a copied name, pseudo inode, parent linkage, optional parent vnode reference, and are inserted into the per-mount hash table under `sm_hashlock`. `smbfs_nget` wraps this with attribute-cache insertion.

Reclaim removes nodes from the hash, clears the root pointer when needed, frees names and node memory, and releases parent references. It also sets `sm_didrele` so unmount can retry `vflush` when parent references were dropped.

Inactive closes any still-open SMB file handle, invalidates buffers, uses cached credentials, and releases them. Attribute-cache helpers store size, mtime, DOS attributes, and attr age; cached attributes expire after roughly two seconds. `smbfs_attr_cacherename` rehashes a node under a new name after successful remote rename.
