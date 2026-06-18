# File Research: sources/os/bsd/openbsd-src/sys/sys/vnode.h

Defines the OpenBSD vnode core. `struct vnode` tracks UVM state, VOP table, vnode type/tag, flags, reference/write/hold counts, mount linkage, buffer trees/lists, sync list, type-specific union, namecache trees, filesystem-private data, and kqueue pollers. Vnode tags include `VT_EXT2FS`, which ext2fs uses.

Also defines `struct vattr`, I/O flags, mode bits, `VNOVAL`, vnode lifecycle flags, and bio flags. Kernel sections declare `struct vops`, all VOP argument structures and wrapper prototypes, global vnode state, type/mode conversion tables, and public vnode/VFS helpers such as `getnewvnode`, `vaccess`, `vflush`, `vget`, `vgone`, `vinvalbuf`, `vrele`, `vref`, `vn_open`, `vn_rdwr`, `vn_stat`, `vn_lock`, syncer helpers, and UVM vnode size/cache hooks.
