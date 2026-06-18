# File Research: sources/os/bsd/freebsd-src/sys/sys/vnode.h

Core FreeBSD vnode interface and VFS operation contract header. It defines vnode types, vnode lifecycle states, `struct vnode`, vnode attributes, I/O flags, access-mode bits, vnode operation descriptors, VOP helper macros, namecache hooks, vnode reference/locking APIs, range-lock wrappers, VM object helpers, and SMR helpers.

Key content:
- Defines `enum vtype` values for regular files, directories, block/char devices, symlinks, sockets, FIFOs, bad vnodes, and marker vnodes.
- Defines `enum vstate` and `enum vgetstate` for vnode construction/recycle/ref acquisition state.
- `struct vnode` is the central active-file object: operation vector, filesystem-private `v_data`, mount linkage, type-specific union, vfs hash linkage, namecache lists, vnode/interlock locks, buffer object, poll/inotify state, MAC label, advisory/range locks, hold/use counts, flags, write count, and sequence counter state.
- Documents lock ownership for vnode fields and list traversal rules: find under list lock, take interlock, drop list lock, then use `vget()` or doomed checks.
- Defines vnode flags split across interlock-protected `VI_*`/`VIRF_*`, vnode-lock-protected `VV_*`/`V2_*`, and mount-list `VMP_*` state.
- Defines `struct vattr` and operation flags such as `VA_UTIMES_NULL`, `VA_EXCLUSIVE`, and `VA_SYNC`.
- Defines I/O flags used by filesystem VOPs: `IO_SYNC`, `IO_ASYNC`, `IO_DIRECT`, `IO_EXT`, `IO_NORMAL`, `IO_BUFLOCKED`, `IO_RANGELOCKED`, sequence hints, and related bits.
- Defines access-mode bits from classic read/write/execute through NFSv4-style ACL permissions.
- Defines `struct vnodeop_desc`, generic VOP argument layout, VOP descriptor flags, and includes generated `vnode_if.h`.
- Declares broad kernel vnode/VFS APIs: namecache operations, vnode allocation/recycle/reference, `vn_open`, `vn_rdwr`, `vn_copy_file_range`, `vn_start_write`, `vn_truncate_locked`, extattr helpers, path helpers, directory iteration, vfs hash, and default/dead VOPs.
- Provides invariant/debug macros around vnode and VOP locking, stat/readdir/write pre/post hooks, kqueue/inotify notification hooks, and checked writecount/text helpers.
- Provides SMR wrappers for VFS read-side lookup and `vn_load_v_data_smr()`.

Research relevance:
- This is the primary vnode ABI/contract file for FreeBSD filesystems.
- FFS code in this group depends on these contracts for vnode locking, buffer objects, VOP dispatch, write suspension, sequence counters, VM objects, and I/O flag interpretation.
- The header is also the best single map of what a FreeBSD filesystem must implement or can delegate to default VOP helpers.
