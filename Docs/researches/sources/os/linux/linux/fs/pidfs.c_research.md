# File Research: sources/os/linux/linux/fs/pidfs.c

## Purpose

`pidfs.c` implements the kernel pseudo filesystem backing pidfds. It gives pidfds stable inode/file identity, poll and ioctl behavior, namespace-fd access, pidfd information retrieval, export-by-file-handle support, trusted xattrs, and lifecycle integration with `struct pid` allocation, task exit, coredump reporting, and pid cleanup.

## Main Responsibilities

- Mount and initialize the internal `pidfs` pseudo filesystem.
- Allocate stable pidfs inode numbers for `struct pid`.
- Maintain an inode-number-to-`struct pid` rhashtable for file-handle decode.
- Create pidfd files from stashed pidfs dentries.
- Provide pidfd file operations: poll, ioctl, release, and proc fdinfo display.
- Expose process namespace file descriptors via pidfd ioctls.
- Expose structured pidfd information through `PIDFD_GET_INFO`.
- Record exit and coredump information in pidfs attributes.
- Support exportfs file handles for live pidfds.
- Provide simple trusted xattr storage tied to pidfs attributes.
- Handle delayed freeing of xattrs after `struct pid` teardown.

## Key Types And Globals

- `pidfs_root_path`: root path of the internal pidfs mount.
- `pidfs_attr_cachep`: slab cache for `struct pidfs_attr`.
- `pidfs_xa_cache`: cache for simple xattr objects.
- `pidfs_ino_ht`: rhashtable keyed by `struct pid.ino`.
- `PIDFS_PID_DEAD`: sentinel used when a pid can no longer be registered with pidfs.
- `struct pidfs_anon_attr`: stores exit and coredump information exposed by pidfd info APIs.
- `struct pidfs_attr`: owns simple xattrs plus anonymous pidfd attributes, or an llist node while queued for deferred free.

## Inode Number Handling

On 64-bit systems, `pidfs_alloc_ino()` uses a cookie generator and the full 64-bit value is the inode number. The generation number is zero.

On 32-bit systems, the 64-bit pidfs identifier is split: lower 32 bits become `i_ino` and upper 32 bits become `i_generation`. If the lower 32 bits wrap to zero, allocation skips forward so inode numbering restarts at one. Userspace can reconstruct stronger identity from inode plus generation or file handles.

`pidfs_add_pid()` assigns an inode number and inserts the pid into `pidfs_ino_ht`; `pidfs_remove_pid()` removes it.

## Pidfd File Operations

`pidfs_file_operations` provides:

- `pidfd_poll()`: waits on `pid->wait_pidfd` and reports readable/hangup state after process exit, avoiding premature notification for delayed group leaders.
- `pidfd_ioctl()`: handles pidfd ioctls.
- `pidfs_file_release()`: implements `PIDFD_AUTOKILL` by sending `SIGKILL` to the target thread group when the pidfd is closed.
- `pidfd_show_fdinfo()`: under procfs, prints `Pid:` and `NSpid:` from the procfs instance pid namespace perspective.

`pidfd_pid()` verifies that a file really uses pidfs file operations before returning its `struct pid`.

## PIDFD_GET_INFO

`pidfd_info()` implements the extensible `PIDFD_GET_INFO` ioctl. It validates userspace struct size, copies the requested mask, rejects tasks outside the caller's pid namespace hierarchy, and returns requested or unconditional fields.

It can report:

- pid/tgid/ppid identifiers
- real/effective/saved/fs uid/gid values mapped into the caller's user namespace
- cgroup id
- exit code and exit cgroup id when exit info is available
- coredump policy/result, signal, and code
- supported mask for feature discovery

If the task has already been reaped, only stored exit information may be available. Memory barriers pair with exit/coredump writers so users see complete stored records.

## Namespace Ioctls

`pidfd_ioctl()` supports namespace accessors for cgroup, IPC, mount, network, pid-for-children, time, time-for-children, UTS, user, and pid namespaces when the corresponding kernel config exists. It obtains the target task, snapshots or references the namespace, checks `ptrace_may_access()` with filesystem credentials, and returns an opened namespace fd via `open_namespace()`.

It also handles `FS_IOC_GETVERSION` by returning the pidfs inode generation number.

## Exit And Coredump State

`pidfs_exit()` runs during task exit. If no pidfd ever registered the pid, it marks `pid->attr` as `PIDFS_PID_DEAD` so later pidfs registration fails instead of creating pidfds for a reaped task without exit info. If attributes exist, it records cgroup id and exit code, issues a write barrier, and sets the exit bit.

`pidfs_coredump()` records coredump mask, signal, and code, then sets the coredump bit after a write barrier.

`pidfs_free_pid()` frees pidfs attributes when the pid is freed. If xattrs are present, it queues the attribute object onto a lockless list and schedules work to free simple xattrs safely.

## Pseudo Filesystem And Dentries

`pidfs_init_fs_context()` initializes a pseudo filesystem with `PID_FS_MAGIC`, `DCACHE_DONTCACHE`, pidfs super operations, export operations, dentry operations, xattr handlers, and stashed-dentry operations.

`pidfs_dname()` returns `anon_inode:[pidfd]` for compatibility with userspace tools that historically saw pidfds as anonymous inodes.

`pidfs_stash_dentry()` ensures the pid is registered before stashing a dentry in `pid->stashed`. `pidfs_alloc_file()` obtains the stashed path, opens it as `O_RDWR`, preserves pidfd-specific internal flags that normal open handling strips, and returns the pidfd file.

## Exportfs Support

`pidfs_encode_fh()` encodes the 64-bit pidfs inode number into a two-word file handle. `pidfs_fh_to_dentry()` decodes live pids by looking up the inode number in `pidfs_ino_ht`, rejecting dead/exited/out-of-namespace pids, and recreating the stashed dentry path.

`pidfs_export_permission()` validates `open_by_handle_at()` flags and relies on pid namespace hierarchy checks in pid lookup. `pidfs_export_open()` normalizes flags and opens pidfds as read-write.

## Xattrs

Pidfs supports trusted xattrs using `simple_xattr_*()` helpers. `pidfs_xattr_get()` and `pidfs_xattr_set()` access xattrs stored in `pid->attr->xattrs`; setting expects the inode lock to serialize list mutation. `pidfs_listxattr()` lists xattrs through the inode operations.

## Initialization

`pidfs_init()` initializes the inode rhashtable, creates the `pidfs_attr_cache`, mounts the internal pseudo filesystem with `kern_mount()`, and stores its root path for later use by pidfs callers.

## Risk Notes

- `pid->attr` has sentinel, NULL, and allocated states; races with exit are synchronized with `pid->wait_pidfd.lock`.
- Exit and coredump information uses memory barriers so readers observe complete records.
- File-handle decode must not resurrect exited or namespace-invisible pids.
- Namespace ioctls require ptrace-style access checks before exposing namespace fds.
- `PIDFD_AUTOKILL` close behavior is intentionally restricted away from kthreads and user workers.
