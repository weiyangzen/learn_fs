# File Research: sources/os/bsd/dragonflybsd/sys/vfs/smbfs/smbfs_node.h

This header defines the SMBFS vnode-private `struct smbnode` and node-level flags. Each node stores parent/vnode/mount pointers, attribute cache data, size, inode, DOS attributes, open count, cached open credential, SMB FID, granted access mode, name, directory search context, last directory offset, record-lock state, and hash linkage.

Important flags include flush serialization bits, `NMODIFIED`, and `NREFPARENT`, which records that the node holds a parent vnode reference. `SMBFS_ROOT_INO` is set to 2.

The header provides conversion macros `VTOSMB` and `SMBTOV` and prototypes for node lifecycle, VM pager hooks, regular read/write helpers, attribute cache helpers, and the name hash function.
