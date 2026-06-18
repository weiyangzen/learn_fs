# File Research: sources/os/bsd/freebsd-src/sys/fs/smbfs/smbfs_node.h

## Purpose

Defines SMBFS vnode-private node state, node flags, vnode conversion macros, and node/I/O helper prototypes.

## Main Interface

`struct smbnode` stores:
- flags for flushing, modified state, parent references, pending wire flush, open state, and removed/renamed state.
- parent vnode and current vnode.
- mount pointer.
- attr cache timestamp, times, size, inode numbers, DOS attrs.
- SMB file id and granted access mode.
- remote path/name buffers and lengths.
- directory search context and offset.
- VFS hash linkage.

`struct smbcmp` is the VFS hash comparison key of parent, name length, and name.

Macros:
- `VTOSMB()`, `SMBTOV()`, `SMBFS_DNP_SEP()`.

Declared functions cover inactive/reclaim, node lookup/allocation, hash, VM page I/O, vnode read/write, and attribute cache operations.

## Integration Points

Shared by SMBFS node, VOP, I/O, VFS, and SMB request files.

## Risks and Review Notes

The node carries both vnode lifecycle state and wire protocol state. Callers must keep `NOPEN`, `n_fid`, directory search context, and parent references synchronized with vnode inactive/reclaim paths.
