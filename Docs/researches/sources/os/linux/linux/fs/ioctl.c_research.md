# File Research: sources/os/linux/linux/fs/ioctl.c

Generic VFS ioctl syscall implementation. It handles common filesystem/file ioctls centrally, falls back to file-specific `->unlocked_ioctl`, and provides compat syscall behavior.

Core paths:
- `vfs_ioctl()` invokes `file_operations->unlocked_ioctl()` and maps `-ENOIOCTLCMD` to `-ENOTTY`.
- `ioctl_fibmap()` implements privileged FIBMAP using `bmap()`, with overflow warning.
- `fiemap_fill_next_extent()` and `fiemap_prep()` are exported helpers for filesystem `->fiemap` implementations.
- `ioctl_fiemap()` copies the user request, validates extent count, calls `inode->i_op->fiemap`, and copies results back.
- Clone/dedupe helpers call `vfs_clone_file_range()` and `vfs_dedupe_file_range()`.
- Legacy XFS preallocation ioctls are translated to `vfs_fallocate()` with `FALLOC_FL_KEEP_SIZE`.

Common ioctl dispatch:
- Handles close-on-exec, nonblocking, async notification, directory/file size query, freeze/thaw, fiemap, block size, clone, dedupe, flags, xflags, filesystem UUID, and filesystem sysfs path.
- Regular non-anon files also receive legacy file ioctls such as FIBMAP and reservation operations.
- The syscall path runs LSM hooks before dispatch.

Compat behavior:
- `compat_ptr_ioctl()` is exported for simple pointer-compatible handlers.
- `compat_sys_ioctl` special-cases `FICLONE`, x86_64 preallocation layout variants, and 32-bit flag ioctl numbers before falling back to generic or file compat handlers.

Risks:
- Any new common ioctl must consider compat argument layout and LSM impact, as the file comment warns.
- User-copy sizes for variable dedupe arrays and FIEMAP extent counts are bounded to avoid overflow or excessive allocation.
- Freeze/thaw requires `CAP_SYS_ADMIN` in the superblock user namespace.
