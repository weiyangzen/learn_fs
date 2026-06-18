# File Research: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore_node.c

Read completely: 258 lines.

Manages FileCore in-core nodes and vnode loading. It owns `filecore_node_pool` and initializes vnodes with a minimal genfs ops table using `genfs_size`.

`filecore_loadvnode()` allocates a node from the pool, records the synthetic inode number, device, mount, and cached device vnode, and either fabricates the root directory entry from the disc record root address or reads the parent directory block and copies the indexed directory entry. It sets vnode tag, operation vector, type (`VDIR` for directory attribute, otherwise `VREG`), root flag, genfs state, and vnode size.

`filecore_inactive()` marks stale nodes for recycling when the directory entry name is zero. `filecore_reclaim()` drops the held device vnode reference, destroys genfs state, returns the node to the pool, and clears `v_data`.
