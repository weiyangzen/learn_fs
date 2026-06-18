# File Research: sources/os/linux/linux/fs/readdir.c

Core VFS directory iteration and `getdents` syscall implementation.

Key responsibilities:
- `wrap_directory_iterator()` adapts filesystems that need exclusive inode locking to the shared `iterate_shared` calling convention.
- `iterate_dir()` performs permission checks, fsnotify permission checks, shared inode locking, `IS_DEADDIR` checks, position transfer, and calls `file->f_op->iterate_shared`.
- `verify_dirent_name()` rejects invalid directory entry names with nonpositive length, path-sized length, or embedded `/`.
- Implements old `readdir` support when `__ARCH_WANT_OLD_READDIR` is enabled.
- Implements `getdents` using `struct linux_dirent` and `filldir()`.
- Implements `getdents64` using `struct linux_dirent64` and `filldir64()`.
- Implements compat old readdir and compat `getdents` under `CONFIG_COMPAT`.

Important behavior:
- Uses `unsafe_put_user` / `unsafe_copy_to_user` within scoped user-write regions for efficient dirent emission.
- Each fill callback validates name and inode-number overflow for ABI-sized inode fields.
- `getdents` and `getdents64` write the final directory offset into the previous record’s `d_off` after iteration.
- Honors `FILLDIR_FLAG_NOINTR` masking and can stop on pending signals after at least one record.
- Updates `file->f_pos`, triggers `fsnotify_access()`, and calls `file_accessed()` after successful iteration.

Research notes:
- This file is the VFS ABI bridge between filesystem `iterate_shared` callbacks and userspace directory-entry record layouts.
