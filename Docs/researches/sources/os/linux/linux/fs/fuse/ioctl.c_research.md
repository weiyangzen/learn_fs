# File Research: sources/os/linux/linux/fs/fuse/ioctl.c

Implements FUSE ioctl dispatch, including unrestricted retry-style deep-copy ioctls, restricted `_IOC_*`-decoded ioctls, compat handling, fs-verity ioctl sizing, and file attribute get/set via private ioctl opens.

Key entry points:
- `fuse_do_ioctl()` builds and submits `FUSE_IOCTL` requests, copies user input pages into request folios, handles server-requested `FUSE_IOCTL_RETRY`, validates returned iovecs, copies output data back to userspace, and returns either transport errors or `outarg.result`.
- `fuse_ioctl_common()`, `fuse_file_ioctl()`, and `fuse_file_compat_ioctl()` are VFS-facing wrappers that enforce connection process permission and bad-inode checks.
- `fuse_fileattr_get()` / `fuse_fileattr_set()` implement `fileattr` support by opening a temporary FUSE file and issuing `FS_IOC_GETFLAGS`, `FS_IOC_SETFLAGS`, `FS_IOC_FSGETXATTR`, or `FS_IOC_FSSETXATTR`.

Important control flow:
- `fuse_send_ioctl()` normalizes `-ENOSYS` to `-ENOTTY`, both as request error and as server result.
- `fuse_copy_ioctl_iovec_old()` supports the legacy ABI where returned iovecs were native/compat `struct iovec`; `fuse_copy_ioctl_iovec()` uses `struct fuse_ioctl_iovec` for protocol minor >= 16 and validates truncation/compat conversions.
- Restricted ioctls prebuild in/out iovecs from `_IOC_DIR` and `_IOC_SIZE`; unrestricted ioctls allow iterative retry with server-provided iovecs.
- `FS_IOC_MEASURE_VERITY` and `FS_IOC_ENABLE_VERITY` receive special setup because their effective buffer lengths are not represented by the basic ioctl size alone.

Dependencies and integration:
- Uses `fuse_simple_request()`, `fuse_folios_alloc()`, `copy_folio_from_iter()`, `copy_folio_to_iter()`, FUSE protocol structs, and VFS fileattr/fs-verity definitions.
- Exports `fuse_do_ioctl()` for other FUSE-related consumers such as CUSE.
- Temporary private ioctl path uses `fuse_file_open()` and `fuse_file_release()`.

Risks and invariants:
- Iovec sizes are bounded by `fc->max_pages << PAGE_SHIFT`; retry count is bounded by `FUSE_IOCTL_MAX_IOV`.
- Restricted mode rejects server retry to prevent arbitrary deep copies.
- Output size larger than advertised `inarg.out_size` is treated as protocol error.
- The function allocates both folio arrays and an iovec page; all exit paths release folios and memory.
