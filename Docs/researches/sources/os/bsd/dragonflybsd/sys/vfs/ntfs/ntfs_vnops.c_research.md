# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_vnops.c

This file implements NTFS vnode operations. It wires `ntfs_vnode_vops` with getattr, inactive, reclaim, pathconf, old lookup, access, open/close, readdir, fsync, bmap, VM get/put pages, strategy, read, and write.

The read path uses cluster-sized `bread()` calls through the vnode/buffer cache. The strategy path maps buffer I/O to `ntfs_readattr()` or `ntfs_writeattr_plain()`. Writes are allowed only within the existing file size; attempts to extend return `EFBIG`.

`ntfs_getattr()` synthesizes Unix attributes from mount uid/gid/mode defaults, fnode size/allocation, ntnode link count, and NTFS file times. `ntfs_access()` checks mount read-only state and applies the mount-provided permission mask rather than per-file NTFS ACLs.

`ntfs_readdir()` simulates `.` and `..`, then converts NTFS Unicode names through `NTFS_U28()` and emits directory entries from `ntfs_ntreaddir()`. `ntfs_lookup()` handles `.`, `..`, and ordinary child lookup through `ntfs_ntlookupfile()`.

Research notes: this vnode layer presents a Unix-like view of NTFS with simplified permissions and limited write behavior. It does not implement create, remove, rename, mkdir, or truncation.
