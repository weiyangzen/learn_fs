# File Research: sources/os/linux/linux-stable/fs/pidfs.c

## Purpose

`pidfs.c` implements the kernel pidfs pseudo filesystem used to back pidfds with real inodes, stable inode/file-handle identity, pidfd polling, pidfd info ioctls, namespace-opening ioctls, pidfd xattrs, and lifecycle hooks for process exit/coredump metadata.

## Main State

- `pidfs_root_path`: root path of the kernel-mounted pidfs instance.
- `pidfs_attr_cachep`: cache for per-pid pidfs attributes.
- `pidfs_ino_ht`: rhashtable mapping 64-bit pidfs inode numbers to `struct pid`.
- `struct pidfs_attr`: per-pid state containing simple xattrs and anonymous pidfd metadata.
- `struct pidfs_anon_attr`: exit and coredump fields exposed by `PIDFD_GET_INFO`.

`PIDFS_PID_DEAD` marks a `struct pid` that was reaped before pidfs registration could provide exit metadata.

## Inode Number Model

On 64-bit systems, pidfs inode numbers are generated as 64-bit cookies and exposed directly.

On 32-bit systems, the lower 32 bits become `i_ino` and upper 32 bits become `i_generation`; zero lower bits are skipped on wraparound. This lets users reconstruct a wider identity using inode plus generation or file handles.

`pidfs_add_pid()` allocates an inode number and inserts the pid into the rhashtable. `pidfs_remove_pid()` removes it.

## Pidfd File Operations

`pidfs_file_operations` provides:

- `poll`: `pidfd_poll()` wakes for process exit, avoiding premature thread-group leader notifications.
- `show_fdinfo`: `pidfd_show_fdinfo()` under procfs, printing `Pid` and `NSpid`.
- `unlocked_ioctl`: `pidfd_ioctl()`.
- `compat_ioctl`: `compat_ptr_ioctl`.
- `release`: `pidfs_file_release()`, which optionally sends `SIGKILL` for `PIDFD_AUTOKILL`.

`pidfd_pid()` validates that a file is a pidfs pidfd and returns its `struct pid`.

## PIDFD_GET_INFO

`pidfd_info()` implements the extensible `PIDFD_GET_INFO` ioctl. It validates structure size, copies the requested mask, restricts information to the caller's pid namespace hierarchy, and returns supported subsets:

- pid/tgid/ppid
- credentials mapped into current user namespace
- cgroup id
- exit code
- coredump mask/signal/code
- supported mask

Exit and coredump info are read from `pidfs_attr` with memory barriers so users see complete records or no record.

## Namespace Ioctls

`pidfd_ioctl()` validates pidfd ioctl commands and supports namespace-opening ioctls for cgroup, IPC, mount, network, pid-for-children, time, UTS, user, and pid namespaces. It gets the target task, checks ptrace read access with filesystem credentials, takes namespace references, and returns namespace file descriptors via `open_namespace()`.

`FS_IOC_GETVERSION` returns inode generation, which matters especially on 32-bit inode identity.

## Exit And Coredump Hooks

`pidfs_exit()` runs during task release. If no pidfd ever registered the pid, it marks the pid dead so future pidfs registration fails. Otherwise it records cgroup id and exit code, then sets the exit bit after a write memory barrier.

`pidfs_coredump()` records coredump disposition, signal, and code, then sets the coredump bit after a write memory barrier.

`pidfs_free_pid()` frees or defers freeing pidfs attributes. If xattrs exist, freeing is queued through an llist and work item so simple xattrs can be released safely.

## Pseudo Filesystem And Export

Pidfs is initialized as a pseudo filesystem with `init_pseudo()`, `PID_FS_MAGIC`, noexec/nodev flags, non-cached dentries, pidfs super ops, export ops, dentry ops, and trusted xattr handlers.

Export support includes:

- `pidfs_encode_fh()`: encodes the 64-bit pidfs inode number.
- `pidfs_fh_to_dentry()`: resolves a handle through the inode rhashtable and stashed dentry mechanism.
- `pidfs_export_permission()`: validates open flags for `open_by_handle_at()`.
- `pidfs_export_open()`: opens pidfd handles as pidfd files.

`pidfs_ino_get_pid()` rejects missing, unregistered, exited, or namespace-invisible pids.

## Dentry And Inode Handling

Pidfs uses stashed dentries to give pidfds stable dentries/inodes. `pidfs_stash_dentry()` ensures pidfs registration before stashing.

`pidfs_init_inode()` initializes inode private data, flags, operations, file operations, inode number, and generation.

`pidfs_evict_inode()` clears the inode and drops the pid reference.

Dentry names are reported as `anon_inode:[pidfd]` to preserve existing userspace expectations such as `lsof`.

## Xattr Support

Pidfs allows trusted xattrs through simple xattr storage. `pidfs_xattr_set()` lazily allocates the xattr container under inode lock, and `pidfs_xattr_get()` / `pidfs_listxattr()` read it. This is intentionally narrow and paired with anon-inode-style setattr/getattr behavior.

## Initialization

`pidfs_init()` initializes the inode rhashtable, creates the pidfs attribute slab cache, kernel-mounts pidfs, and records the root path.

## Risk Notes

- Exit/coredump info publication relies on memory ordering around attr bits.
- Namespace ioctl access control depends on pid namespace visibility plus ptrace filesystem-credential checks.
- File-handle reopen must reject stale/exited pids to avoid resurrecting invalid pidfds.
- `PIDFD_AUTOKILL` release behavior is powerful and intentionally excludes kernel threads/user workers.
