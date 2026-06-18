# File Research: sources/os/bsd/dragonflybsd/sys/sys/vfscache.h

## Summary
VFS cache-facing vnode type, tag, and attribute definitions.

## Main Responsibilities
- Defines vnode types such as regular, directory, block/char device, symlink, socket, FIFO, database, and internal.
- Defines external vnode tag identifiers for filesystem families, including HAMMER, HAMMER2, devfs, tmpfs, autofs, and FUSE.
- Defines full `struct vattr` and lightweight `struct vattr_lite`.
- Defines vattr operation flags for null utimes, exclusive create, and UUID validity.

## Important Behavior
`VNOVAL` semantics are described externally in `vnode.h`, but `vattr` fields here are the primary VOP getattr/setattr payload. `vattr_lite` is explicitly tied to fast-path getattr and futimes code.

## Risks
Kernel code must not use `vtagtype` for behavior decisions; comments say tags are for external tools. Any `vattr_lite` layout changes must be synchronized with fast-path users named in the comments.
