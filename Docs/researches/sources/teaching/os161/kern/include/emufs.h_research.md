# File Research: sources/teaching/os161/kern/include/emufs.h

Defines private in-memory structures for the emulated host filesystem.

Key structures:
- `struct emufs_vnode` wraps a generic vnode, emu device pointer, and host-side file handle.
- `struct emufs_fs` wraps generic FS, emu device pointer, root vnode, and loaded vnode table.

Relevance:
- Parallel example of an OS/161 filesystem implementation that shares the same `fs`/`vnode` abstraction as SFS and semfs.
