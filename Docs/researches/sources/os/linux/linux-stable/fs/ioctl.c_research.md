# File Research: sources/os/linux/linux-stable/fs/ioctl.c

This file implements the generic VFS ioctl syscall path and common filesystem/file ioctl commands before dispatching to filesystem-specific handlers.

Key responsibilities:
- Provides `vfs_ioctl()` wrapper for `file_operations->unlocked_ioctl`, translating `-ENOIOCTLCMD` to `-ENOTTY`.
- Implements privileged `FIBMAP` handling through `bmap()` and `CAP_SYS_RAWIO`.
- Implements FIEMAP helpers: `fiemap_fill_next_extent()`, `fiemap_prep()`, and `ioctl_fiemap()`.
- Implements file clone and clone-range ioctls through `vfs_clone_file_range()`.
- Implements legacy XFS-style preallocation ioctls through `vfs_fallocate()`.
- Handles `FIONBIO`, `FIOASYNC`, `FIOQSIZE`, filesystem freeze/thaw, dedupe range, filesystem UUID, and filesystem sysfs path ioctls.
- Dispatches generic ioctls in `do_vfs_ioctl()` and falls back to file-specific or filesystem-specific ioctl handlers.
- Implements native `sys_ioctl` and compat `compat_sys_ioctl`.
- Exports `compat_ptr_ioctl()` for file operations whose ioctl arguments are pointer-compatible between native and compat modes.

Important interactions:
- Calls LSM hooks `security_file_ioctl()` and `security_file_ioctl_compat()` before ioctl dispatch.
- Uses file attribute helpers from `fileattr.h` for `FS_IOC_GETFLAGS`, `FS_IOC_SETFLAGS`, `FS_IOC_FSGETXATTR`, and `FS_IOC_FSSETXATTR`.
- Coordinates freeze/thaw through superblock operations or generic `freeze_super()` / `thaw_super()`.
- Uses `copy_from_user()`, `copy_to_user()`, `get_user()`, and `put_user()` heavily because this is the syscall boundary.

Notable invariants and risks:
- `FIEMAP_MAX_EXTENTS` avoids 32-bit overflow in extent array sizing.
- `FICLONE` takes an integer fd argument, so compat handling must not blindly `compat_ptr()` it.
- Dedupe range allocation is capped to one page.
- `FIONREAD` for regular files reports `i_size - f_pos`, while non-regular and anonymous cases dispatch to file-specific ioctl handling.
- New common ioctls must be audited for compat layout and LSM impact, as noted in the file comments.

Research notes:
- This is the generic ioctl funnel for VFS. It standardizes common file/filesystem commands and isolates compat-specific traps before invoking filesystem-private ioctl code.
