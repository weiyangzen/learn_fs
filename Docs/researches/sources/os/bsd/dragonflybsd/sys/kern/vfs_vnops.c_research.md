# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_vnops.c

Read completely: 1352 lines.

This file implements DragonFlyBSD's file-object-facing vnode operations. It provides `vnode_fileops` methods for open-backed file descriptors: read, write, ioctl, kqueue filter, stat, close, and seek.

Key responsibilities:
- `vn_open()` performs namecache lookup, create/open/truncate handling, permission/write checks, vnode locking, FUSE flag propagation, `VOP_NCREATE`, `VOP_OPEN`, and file pointer setup.
- `vn_rdwr()` and `vn_rdwr_inchunks()` package kernel read/write requests into `uio` structures, optionally splitting large I/O to avoid buffer-cache pressure.
- `vn_read()` and `vn_write()` translate file flags into VOP I/O flags, serialize shared file offsets with `FOFFSETLOCK`, apply sequential access heuristics, and call `VOP_READ_FP`/`VOP_WRITE_FP`.
- `vn_stat()` converts `vattr` data into `struct stat`, including device vnode timestamps, block size selection, generation-number privilege filtering, and ABI compatibility fields.
- `vn_ioctl()` handles generic vnode ioctls such as `FIONREAD`, `FIOASYNC`, `FIODTYPE`, forwards to `VOP_IOCTL`, and updates controlling tty state after `TIOCSCTTY`.
- `vn_lock()`, `vn_unlock()`, `vn_islocked*()` centralize vnode lock behavior and reclaimed-vnode checks.
- `vn_bmap_seekhole*()` implements `FIOSEEKHOLE`/`FIOSEEKDATA` through `VOP_BMAP`.
- `vn_seek()` implements `lseek`, including `SEEK_DATA` and `SEEK_HOLE`.

Important interactions:
- Depends on namecache/nlookup state, `VOP_*` vnode operations, mount write checks, quotas/accounting, file descriptor state, and buffer-cache backpressure helpers.
- `vn_open()` transfers `nd->nl_nch` into `fp->f_nchandle` when a file pointer is supplied.
- Write/truncate paths use both namecache-level `ncp_writechk()` and vnode-level `vn_writechk()` to account for nullfs/cross-mount cases.

Security/reliability notes:
- Open/create correctness depends on careful vnode/namecache lock handoff and ESTALE retry behavior.
- Offset serialization intentionally allows some heuristic races but protects `f_offset` integrity for normal shared-file reads/writes.
- Negative offsets are rejected for regular files and directories but allowed for special devices for 64-bit kvm-style address use.
