# File Research: sources/teaching/os161/kern/include/sfs.h

Public kernel header for SFS.

Key structures:
- `struct sfs_vnode` embeds generic vnode, in-memory copy of on-disk dinode, inode number, and dirty flag.
- `struct sfs_fs` embeds generic FS, superblock copy, dirty flags, mounted device, resident vnode table, freemap bitmap, and freemap dirty flag.

Key API:
- `sfs_mount(const char *device)`.

Dependencies:
- Includes generic FS/vnode abstractions and shared on-disk format from `<kern/sfs.h>`.

Relevance:
- This is the kernel-visible contract used by SFS implementation files and VFS mount registration.
