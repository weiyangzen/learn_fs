# File Research: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_vnops.c

Implements FreeBSD vnode operations for the kernel FUSE filesystem bridge. It maps VFS operations onto FUSE protocol requests, manages vnode/filehandle state, handles cache coherency, and integrates FUSE with FreeBSD permissions, buffer cache, VM pager, NFS export support, xattrs, locking, and sparse-file interfaces.

Main responsibilities:
- Registers `fuse_vnops` for normal FUSE vnodes and `fuse_fifoops` for FIFO special handling.
- Implements VOPs for access, lookup, create, mknod, mkdir, symlink, link, rename, remove, rmdir, open, close, inactive, reclaim, read, write, readdir, readlink, fsync/fdatasync, getattr/setattr, bmap, strategy, getpages, pathconf, advlock, ioctl, xattrs, allocate/deallocate, delayed setsize, print, and NFS filehandle export.
- Uses FUSE feature probing and fallback: `FUSE_CREATE` fallback to `MKNOD+OPEN`, optional `FUSE_BMAP`, `FUSE_LSEEK`, `FUSE_FALLOCATE`, `FUSE_COPY_FILE_RANGE`, and xattr opcodes.
- Maintains attribute and entry cache validity, with explicit cache purges after namespace mutations and local size/timestamp changes.

Key implementation details:
- Dead-session checks generally return `ENXIO` with extended error context, while root getattr has a minimal fallback so path-based unmount can still work.
- `fuse_vnop_lookup()` uses FreeBSD namecache timeouts, handles `"."` and `".."`, validates server node ids, creates vnodes via `fuse_vnode_get()`, and enforces sticky/write checks when default permissions are active.
- `fuse_vnop_create()` can receive both entry and open-handle data from `FUSE_CREATE`; if vnode creation fails it sends `FUSE_RELEASE` for the opened handle.
- Read/write choose direct or buffered backends based on `IO_DIRECT`, `FN_DIRECTIO`, and mount data-cache options.
- Buffer invalidation around allocate/deallocate/copy/write preserves dirty partial blocks by flushing edge buffers before invalidating whole buffer ranges.
- `fuse_vnop_close()` sends `FUSE_FLUSH`, opportunistically persists atime, and saves delayed size changes.
- `fuse_vnop_inactive()` flushes or invalidates dirty regular-file buffers before closing all filehandles, then recycles revoked vnodes.
- `fuse_vnop_reclaim()` sends `FUSE_FORGET` for non-root nodes with positive lookup counts, purges cache/hash entries, and destroys vnode-private data.
- xattr VOPs translate FreeBSD `user`/`system` namespaces to Linux/FUSE `user.name` and `system.name` strings; list conversion rewrites NUL-delimited Linux names into FreeBSD length-prefixed names.
- NFS export support requires `FSESS_EXPORT_SUPPORT` and rejects kernel NFS export when the daemon implements `FUSE_OPENDIR`.

Important dependencies:
- FUSE helpers from `fuse.h`, `fuse_file.h`, `fuse_internal.h`, `fuse_ipc.h`, `fuse_node.h`, and `fuse_io.h`.
- FreeBSD VFS/vnode, namecache, buffer cache, VM pager, credential/privilege, extattr, and SDT tracing APIs.
- `fuse_internal_*` routines perform most request construction, permission, setattr, entry validation, fsync, readdir, remove/rename, and vnode cache updates.

Notable risks and edge cases:
- Several operations depend on daemon protocol capability and intentionally degrade to `ENOSYS`, `EOPNOTSUPP`, `ENOTTY`, or local VFS fallbacks.
- Cached attributes can be stale by design; the code carefully chooses when stale cached size is acceptable for advisory clustering.
- FUSE protocol limitations require guessed bmap runs, synthesized `_PC_MIN_HOLE_SIZE`, xattr format conversion, and local validation of server-returned node ids.
- Direct I/O flag reads are explicitly done without a lock, with a referenced FreeBSD bug comment.
