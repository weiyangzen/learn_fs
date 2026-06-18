# File Research: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_vnops.c

This file implements DragonFlyBSD vnode operations for the in-kernel FUSE filesystem bridge. It translates VOP calls into FUSE protocol IPC requests, maintains cached vnode/node state, and integrates FUSE regular-file I/O with DragonFly’s buffer cache, VM pager, namecache, kqueue, locking, and vnode lifecycle.

Main responsibilities:
- Attribute translation and caching via `fuse_set_attr()`, mapping FUSE `struct fuse_attr` into DragonFly `struct vattr`.
- Permission and metadata operations: `access`, `getattr`, `setattr`, `pathconf`.
- File-handle lifecycle: `open`, `close`, `fsync`, `inactive`, `reclaim`, and `fuse_release()`.
- Namecache-backed namespace operations: lookup/resolve, link, create, mknod, unlink, mkdir, rmdir, rename, symlink, readlink, and readdir.
- Regular file read/write through buffer-cache blocks, with VM shortcut reads and size-extension/truncation handling.
- Strategy I/O queuing to a FUSE helper thread so sensitive kernel contexts, including pageout, do not block directly on userland FUSE IPC.
- kqueue filter support for read/write/vnode notifications.
- VM pager glue through generic vnode getpages/putpages.

Key implementation details:
- Most operations first check `fuse_test_dead()` and `fuse_test_nosys()` to gracefully handle dead mounts or unsupported FUSE opcodes.
- `fuse_vop_open()` lazily obtains a FUSE file handle if the node lacks one, using `FUSE_OPENDIR` for directories and `FUSE_OPEN` otherwise. `O_CREAT` is stripped when reopening an already-created vnode.
- `fuse_vop_close()` does not immediately release the FUSE handle. It requests vnode finalization when clean, because the vnode may still be active through directory state, mmap, or other references.
- `fuse_vop_fsync()` flushes DragonFly dirty buffers first, clears `sizeoverride`, may finalize closed vnodes, then sends `FUSE_FSYNC` or `FUSE_FSYNCDIR`.
- `fuse_vop_getattr()` refreshes attributes only when `fnp->attrgood` is clear, otherwise it serves cached attributes. Root ENOTCONN has a fallback minimal attribute response.
- `fuse_vop_setattr()` builds a `FUSE_SETATTR` request from DragonFly `vattr` changes, including size, uid/gid, mode, and timestamps. Unsupported flags return `EOPNOTSUPP`.
- Lookup uses `FUSE_LOOKUP`, creates/locates a `fuse_node`, sets the namecache vnode, and tracks `nlookup` except for `"."`, `".."`, and root-style cases.
- Create-like namespace operations consume `fuse_entry_out`, validate vnode type, allocate a node, cache returned attributes, update namecache, and emit knotes.
- Remove and rename attempt to release unopened target handles early to avoid `.fuse_hidden*` behavior, though comments note that simple `v_opencount` does not fully account for mmap/file pointer cases.
- `fuse_vop_readdir()` requests a large directory buffer and converts FUSE directory entries into DragonFly dirents using `vop_write_dirent()`.
- `fuse_vop_read()` uses `vop_helper_read_shortcut()` first, then falls back to buffer-cache block reads through `cluster_readx()` or `bread_kvabio()`.
- `fuse_vop_write()` enforces max file size and process file-size limits, extends the file through `fuse_reg_resize()`, manages partial/full block overwrite behavior, writes via buffer cache, updates dirty/modified flags, and clears setuid/setgid when required.
- `fuse_vop_strategy()` queues reads/writes on `fmp->bioq`; `fuse_io_thread()` drains the queue and `fuse_io_execute()` performs actual `FUSE_READ`/`FUSE_WRITE` IPC.
- `fuse_bmap()` presents file storage as contiguous to support clustering even though actual backing I/O is RPC-based.
- `fuse_reg_resize()` updates in-memory size, marks `sizeoverride`, and uses `nvtruncbuf()`/`nvextendbuf()` for VM/buffer object resizing.

Important dependencies:
- FUSE core types and helpers from `fuse.h`, including IPC allocation/fill/tx/put helpers.
- DragonFly VFS/namecache APIs: `cache_setvp`, `cache_unlink`, `cache_rename`, vnode finalization, vnode dirty state, and VOP helpers.
- Buffer cache and clustering APIs: `getblk`, `bread_kvabio`, `cluster_readx`, `cluster_write`, `vn_cache_strategy`.
- VM pager APIs: generic vnode pager getpages/putpages and object cleaning.
- kqueue/knote APIs for event delivery.

Notable risks and edge cases:
- Several unsupported or partially-used FUSE protocol fields are explicitly left unused.
- `FUSE_FORGET` paths are disabled because comments state sshfs fails when they are issued.
- Directory reading requests all entries at once with a fixed large buffer; the comment flags this as a limitation.
- Rename/remove cleanup relies on `v_opencount`, with comments warning this misses mmap and file-pointer subtleties.
- Strategy write error handling maps FUSE write failures to `EINVAL` on the buffer rather than preserving the exact FUSE error.
