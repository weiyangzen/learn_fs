# File Research: sources/os/bsd/netbsd-src/lib/libpuffs/pnode.c

This file provides puffs node allocation, list management, accessors, and `puffs_newinfo` setters. `puffs_pn_new` allocates and zeroes a `struct puffs_node`, stores private data and mount pointer, initializes `pn_va` with `puffs_vattr_null`, inserts the node in the mount's pnode list, and marks the mount with `PUFFS_FLAG_PNCOOKIE`.

`puffs_pn_remove` removes a node from the mount list and marks it `PUFFS_NODE_REMOVED`; `puffs_pn_put` frees a node, first freeing its path object with the mount's path-free callback and removing it from the list if it was not already removed. This means removed nodes are still freed through the common put path but are not removed twice.

`puffs_pn_nodewalk` linearly walks the mount's pnode list, using next-pointer prefetch before invoking the callback so callbacks can safely remove the current node. A non-NULL callback return value stops the walk and is returned to the caller.

The rest of the file exposes small accessors for vattr, private data, path object, mount, and mount-specific private data. `puffs_newinfo_setcookie`, `setvtype`, `setsize`, `setrdev`, `setva`, `setvattl`, and `setcnttl` fill kernel-return fields through pointers held in `struct puffs_newinfo`.
