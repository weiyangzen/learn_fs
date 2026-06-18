# File Research: sources/os/bsd/openbsd-src/sys/miscfs/fuse/fusefs_node.h

Purpose: Defines FUSE per-vnode node state and file-handle bookkeeping.

Key contents:
- `enum fufh_type` represents invalid, read-only, write-only, read/write, and max FUSE file handle slots.
- `struct fusefs_filehandle` stores daemon handle ID and slot type.
- `struct fusefs_node` stores hash linkage, vnode pointer, mount pointer, device, inode number, parent cache, byte-range lock state, recursive vnode lock, three FUSE file handles, and cached file size.
- Defines `ITOV()` and `VTOI()` conversion macros.
- Declares FUSE inode hash functions and `fusefs_fd_get()`.

Filesystem relevance:
- This is the per-inode state backing all FUSE vnode operations and hash-cache lookup.
