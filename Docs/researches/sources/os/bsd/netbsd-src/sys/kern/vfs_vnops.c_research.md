# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_vnops.c

Read completely: 1672 lines.

## Purpose
Implements vnode-backed `fileops` and common vnode operation wrappers: open, close, read/write, readdir, stat, ioctl, mmap, seek, advisory locks, pathconf, fadvise, truncate, vnode locking, extended attributes, block-device open helpers, FIFO bypass, and vnode kqueue attachment bookkeeping.

## Main Interfaces
- Fileops table: `vnops` with `vn_read`, `vn_write`, `vn_ioctl`, `vn_fcntl`, `vn_poll`, `vn_statfile`, `vn_closefile`, `vn_kqfilter`, `vn_mmap`, `vn_seek`, `vn_advlock`, `vn_fpathconf`, `vn_posix_fadvise`, `vn_truncate`.
- Open/close helpers: `vn_open`, `vn_openchk`, `vn_writechk`, `vn_close`.
- I/O helpers: `vn_rdwr`, `vn_readdir`, `vn_read`, `vn_write`, `enforce_rlimit_fsize`.
- Metadata/control: `vn_stat`, `vn_ioctl`, `vn_fcntl`, `vn_poll`, `vn_kqfilter`, `vn_lock`.
- Mapping and advice: `vn_mmap`, `vn_seek`, `vn_posix_fadvise`.
- Attributes/devices/events: `vn_extattr_get`, `vn_extattr_set`, `vn_extattr_rm`, `vn_fifo_bypass`, `vn_bdev_open`, `vn_bdev_openpath`, `vn_knote_attach`, `vn_knote_detach`.

## State And Control Flow
`vn_open` performs common namei-based open/create handling. It manages create-vs-lookup paths, `O_EXCL`, `O_NOFOLLOW`, veriexec checks, `VOP_CREATE`, `VOP_OPEN`, truncation, writecount increments, and special `EDUPFD`/`EMOVEFD` file descriptor returns. `vn_openchk` enforces vnode type and read/write/execute access.

`vn_read` and `vn_write` translate file flags into `IO_*` flags, lock the vnode appropriately, set `uio_offset`, call `VOP_READ` or `VOP_WRITE`, and update offsets only when requested. Writes enforce `RLIMIT_FSIZE` for regular files and send `SIGXFSZ` before returning `EFBIG`.

`vn_mmap` validates vnode types and offset overflow, handles `/dev/zero`, defaults missing sharing mode, normalizes private device mappings to shared, computes max protections from file open mode and file flags, rejects noexec executable mappings, calls `VOP_MMAP` or `udv_attach`, marks executable and writable mappings, and integrates veriexec checks.

## Dependencies And Integration
Depends on file descriptors, namei, vnode operations, mount flags, kauth credentials, veriexec, WAPBL diagnostics, UVM objects/device mappings/readahead, specfs, fifofs, tty session vnode tracking, kqueue knotes, and extended attribute VOPs.

## Risks And Edge Cases
- `vn_open` has compatibility handling around `NONEXCLHACK`, `O_CREAT`, and missing `ni_dvp`; cleanup paths must release parent and leaf vnodes correctly.
- Writecount and text/executable mapping flags enforce `ETXTBSY` behavior and executable-page accounting.
- Directory reads have union-mount fallback paths and can mutate `fp->f_vnode`/offset when crossing to the covered vnode.
- `FIONREAD` on directories reads `fp->f_offset` under the file lock; block mapping ioctls translate logical blocks through `VOP_BMAP`.
- `vn_mmap` must keep `maxprot`, `VV_MAPPED`, `VI_WRMAP`, and `VI_EXECMAP` coherent with vnode and UVM state.
- `POSIX_FADV_DONTNEED` shrinks ranges to page boundaries before calling `VOP_PUTPAGES`, so sub-page ranges can be no-ops.
- Knote attach/detach maintains an interest bitmask to avoid unnecessary vnode event traversal.

## Filesystem Relevance
High. This file is the reusable vnode-as-file implementation used by regular files, directories, devices, fifos, mmap, fadvise, directory reads, and many descriptor operations.
