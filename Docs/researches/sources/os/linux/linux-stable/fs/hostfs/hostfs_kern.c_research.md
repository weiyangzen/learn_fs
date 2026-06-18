# File Research: sources/os/linux/linux-stable/fs/hostfs/hostfs_kern.c

## Purpose

Implements the UML `hostfs` filesystem on the Linux VFS side, mapping VFS operations to host-path syscall wrappers.

## Main Entry Points

Defines superblock operations, inode operations for files/directories/symlinks, file operations, address-space operations, fs_context operations, and module init/exit for the `hostfs` filesystem type.

## Control Flow And State

Mount state stores a `host_root_path`. Inode state stores a shared host fd, accumulated open mode, host device identity, birth time, and an open mutex. Path construction uses `dentry_path_raw()` and prefixes the configured host root.

Open upgrades the inode’s shared host fd to cover requested read/write modes, using `dup2()` through `replace_file()` when needed. Read/write page-cache paths call `read_file()` and `write_file()` at folio offsets. Directory iteration opens the host directory for each readdir, seeks to `ctx->pos`, emits entries, and closes it.

Inode instantiation uses `stat_file()` plus `iget5_locked()` keyed by inode number, device, file type, and birth time. Create/mkdir/mknod/link/unlink/symlink/rmdir/rename delegate to host wrappers and then instantiate or update dentries. `hostfs_permission()` combines host `access()` with generic permission. `hostfs_setattr()` translates VFS `iattr` fields to `hostfs_iattr`, suppressing size truncation in append mode.

Mount parsing appends mount-supplied paths to the global `root_ino` prefix. The root inode follows symlinks once if the root path resolves to a symlink.

## Dependencies

Depends on UML setup hooks, the syscall wrappers declared in `hostfs.h`, Linux fs_context, page cache helpers, generic VFS permission/setattr helpers, and a kmem cache for hostfs inodes.

## Risks

Path confinement relies on string prefixing and host filesystem permissions. Append mode blocks unlink and truncation but does not make the whole filesystem immutable. The shared inode fd model requires careful mode upgrades and mutex use. `hostfs_kill_sb()` frees `s_fs_info` directly while `hostfs_fc_free()` also frees fs_context state; mount lifecycle must preserve ownership.
