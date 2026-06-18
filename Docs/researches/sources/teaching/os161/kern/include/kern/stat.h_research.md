# File Research: sources/teaching/os161/kern/include/kern/stat.h

Defines the ABI `struct stat`.

Fields:
- Essential: size, mode, link count, block count.
- Identity: device, inode, raw device.
- Timestamps: atime, ctime, mtime seconds and nanoseconds.
- Permissions: uid, gid.
- Other: generation and preferred block size.

Relevance:
- SFS and semfs fill a subset of these fields in vnode `stat` operations, leaving unsupported fields zeroed.
