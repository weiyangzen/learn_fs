# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_file.c

## Role

`vdev_file.c` implements file-backed leaf vdev operations. It lets ZFS use regular files as vdevs, primarily for testing or non-production configurations, and provides a userland fallback where disk vdevs are accessed like files.

## Main Behavior

Open and close:
- `vdev_file_open()` requires an absolute path.
- File vdevs are marked non-rotational.
- TRIM is allowed as an attempted file-space punch operation, while secure TRIM is disabled.
- Files are opened from the global-zone root using `vn_openat()`.
- In kernel builds, the vnode must be a regular file.
- Physical size is taken from `VOP_GETATTR(AT_SIZE)`.
- `ashift` is set to `SPA_MINBLOCKSHIFT`.
- `vdev_file_close()` invalidates pages with `VOP_PUTPAGE(B_INVAL)`, closes the vnode, releases it, frees `vdev_file_t`, and clears delayed close.

I/O:
- `vdev_file_io_start()` handles:
  - `DKIOCFLUSHWRITECACHE` by calling `VOP_FSYNC(FSYNC | FDSYNC)`.
  - `ZIO_TYPE_TRIM` by issuing `VOP_SPACE(F_FREESP)` over the zio range.
  - reads/writes by creating a `buf_t`, borrowing an ABD buffer, and dispatching `vdev_file_io_strategy()` to `system_taskq`.
- `vdev_file_io_strategy()` performs `vn_rdwr()` at the logical block offset and completes the buf.
- `vdev_file_io_intr()` maps buf errors to `EIO`, maps successful residuals to `ENOSPC`, returns ABD buffers, frees the wrapper, and delays zio interrupt.
- `vdev_file_io_done()` is empty.

Ops:
- `vdev_file_ops` is a leaf vdev type with default asize and xlate behavior.
- In non-kernel builds, `vdev_disk_ops` aliases the same file-backed implementation.

## Integration Notes

This file bridges ZIO to vnode operations rather than LDI strategy calls. It uses ABD borrowing/copying, vnode read/write/fsync/space calls, taskq dispatch, and standard vdev open/close/asize hooks.

## Risk Notes

- File vdev paths must be absolute.
- Kernel file vdevs reject non-regular vnode types.
- Residual writes are reported as `ENOSPC`, unlike disk vdev residuals which become `EIO`.
- TRIM depends entirely on underlying filesystem support for `F_FREESP`.
- File-backed vdev semantics differ from disks for caching, allocation, flush, and failure behavior.
