# File Research: sources/os/bsd/dragonflybsd/sys/sys/vfsops.h

## Summary
Defines DragonFly BSD vnode operation argument structures, VOP operation vectors, wrapper prototypes, descriptors, and convenience macros.

## Main Responsibilities
- Defines per-operation argument structures for old path-based VOPs, file operations, metadata operations, VM/page operations, ACL/extattr operations, mount control, allocation, and namecache-based new VOPs.
- Defines `struct vop_ops`, the per-mount vnode operation vector.
- Declares wrapper functions `vop_*()` and lower-level `*_ap()` forwarding entry points.
- Declares descriptor symbols consumed by generated/compiled vnode operation vectors.
- Defines `VOP_*` convenience macros for common kernel call sites.

## Important Behavior
The file strongly requires callers to use wrapper helpers instead of direct vector calls so future/message-based VFS dispatch and cache/journal hooks can interpose. New namecache VOPs use `struct nchandle` as the operational basis, while old VOPs are deprecated and intended only for compatibility glue.

## Risks
This is a central VFS ABI. A visible issue in this file is the `VOP_FDATASYNC` macro expanding through `VOP_FDATASYNC_FP(*(vp)->v_ops, vp, waitfor, flags, NULL)`, which does not match the `VOP_FDATASYNC_FP(vp, waitfor, flags, fp)` macro shape and appears typo-prone. Operation signatures and descriptor offsets must stay exactly synchronized with generated VOP code.
