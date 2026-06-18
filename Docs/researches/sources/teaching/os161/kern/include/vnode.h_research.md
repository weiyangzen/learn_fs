# File Research: sources/teaching/os161/kern/include/vnode.h

Defines OS/161’s abstract file object. `struct vnode` carries a reference count protected by a spinlock, an owning filesystem pointer, filesystem-specific data, and a `vnode_ops` dispatch table. Device vnodes may have `vn_fs == NULL`.

`struct vnode_ops` covers open/reclaim, read/write/readlink/getdirentry/ioctl/stat/type/seek/fsync/mmap/truncate/namefile, creation/removal/link/rename operations, and lookup/lookparent. `VOP_*` macros validate the vnode with `vnode_check` then dispatch through the table.

The header also exports reference manipulation, initialization/cleanup, and many typed failure stubs for unsupported operations. Main invariants: ops magic must match `VOP_MAGIC`, refcounts must remain positive while in use, and filesystems must return referenced vnodes from lookup-style operations.
