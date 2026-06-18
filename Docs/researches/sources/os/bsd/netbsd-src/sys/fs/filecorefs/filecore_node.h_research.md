# File Research: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore_node.h

Read completely: 133 lines.

Defines the in-core FileCore node. `struct filecore_node` embeds genfs state, vnode/device identity, synthetic inode number, cached physical block, cached parent inode, mount pointer, advisory lock pointer, directory lookup offset, and the copied FileCore directory entry.

The node exposes `i_size` as the directory entry length and defines stale-node detection as an empty directory-entry name. It also declares vnode operation prototypes and utility helpers for mode conversion, timestamp conversion, parent lookup, filename conversion/comparison, and directory block reads.
