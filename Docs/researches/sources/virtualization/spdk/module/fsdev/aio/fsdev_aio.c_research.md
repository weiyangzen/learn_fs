# File Research: sources/virtualization/spdk/module/fsdev/aio/fsdev_aio.c

Implements an SPDK fsdev module backed by a local host filesystem.

Key elements:
- Defines file object and file handle structures wrapping file descriptors, directory state, parent/leaf relationships, refcounts, and locks.
- Creates an `aio_fsdev` rooted at a configured host path.
- Uses `O_PATH`, `openat`, `fstatat`, `linkat`, `renameat`, `unlinkat`, and `/proc/self/fd` to operate relative to tracked file descriptors.
- Provides fsdev handlers for mount, umount, lookup, forget, getattr, setattr, readlink, symlink, mknod, mkdir, unlink, rmdir, rename, link, open, release, read, write, statfs, fsync, xattr operations, flush, directory operations, flock, create, abort, fallocate, and copy-file-range.
- Uses `spdk_aio_mgr` for asynchronous read/write and a poller per I/O channel.
- Has `skip_rw` mode that completes reads/writes without touching backing storage.
- Registers fsdev module `aio` with module init/fini and context size.
- Writes replayable config JSON through `fsdev_aio_create`.
- Exposes `spdk_fsdev_aio_get_default_opts()`, `spdk_fsdev_aio_create()`, and `spdk_fsdev_aio_delete()`.

Dependencies:
- SPDK fsdev module APIs, thread/poller APIs, AIO manager abstraction, POSIX filesystem APIs, xattr APIs, and generated config constants.

Research notes:
- Path traversal is constrained by safe single-component checks for mutating operations; lookup permits `.` and `..` for NFS-export behavior but maps root `..` to root.
- Creation temporarily switches effective uid/gid to request credentials.
- Extended attribute behavior is guarded by `xattr_enabled`; the create path logs that xattrs can only be enabled on Linux but returns the current `rc`, which is zero after prior setup, making that branch worth checking.
