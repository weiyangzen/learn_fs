# sources/user-network-fs/libfuse/util/fusermount.c

## Purpose
Setuid-capable `fusermount3` helper for mounting and unmounting FUSE filesystems on Linux. It enforces non-root policy, opens `/dev/fuse`, performs traditional or new-API mounts, sends the FUSE fd back to libfuse, and optionally daemonizes for auto-unmount.

## Important APIs, Types, And Functions
- Option parsing in `main` handles mount, unmount, lazy, quiet, auto-unmount, comm-fd, and sync-init modes.
- `mount_fuse`, `mount_fuse_prepare`, `mount_fuse_sync_init`, and `mount_fuse_finish_fsmount` implement traditional and split new-API flows.
- `check_perm`, `pin_mountpoint`, `check_nonroot_dir_access`, and `check_nonroot_fstype` validate non-root mountpoints.
- `prepare_mount`, `perform_mount`, `do_mount`, and `mount_notrunc` parse options and perform `mount(2)`.
- `send_fd` and `wait_for_signal` implement Unix fd-passing IPC.
- `unmount_fuse`, `may_unmount`, `check_is_mount`, and `should_auto_unmount` handle unmount safety.

## Control Flow
Mount mode resolves the mountpoint, validates the communication socket, opens `/dev/fuse` under dropped fs privileges, reads config, enforces mount limits, splits `x-` options, validates and pins the mountpoint, then performs a traditional mount or sync-init new mount. The helper sends the FUSE fd over `_FUSE_COMMFD`; in sync-init it waits for the library to signal that the worker is ready before completing the mount. Auto-unmount mode daemonizes, closes inherited fds except the control socket, waits for socket EOF, checks for an abandoned disconnected mount, and lazily unmounts only then.

## State And Persistence
Persistent effects are kernel mounts and mtab/utab updates. Process state includes global `progname` and `auto_unmount`, current working directory changes, fsuid/fsgid switching, and a daemon process for auto-unmount. It intentionally passes file descriptors over Unix sockets.

## Dependencies And Integration Points
Called by `mount.c` fallback and by users directly. Shares `mount_util.c`, `mount_fsmount.c`, and `fuser_conf.c`. Requires `/dev/fuse`, `/proc/mounts`, clone with `CLONE_NEWNS` for mount checks, and optionally `close_range`.

## Risks
This is security-sensitive setuid code. Correctness depends on mountpoint pinning, namespace-based unmount checks, avoiding option truncation, filtering unsafe options for non-root users, and balancing privilege drops. The code comments explicitly acknowledge a residual race in service-style fstat-to-mount scenarios; this helper mitigates many path swaps with pinned fds, especially in sync-init mode. Close-fd logic redirects stdio to `/dev/null`, so diagnostics after daemonization are limited.

## Test Signals
Privilege tests should cover non-root mount over dir/file, sticky directories, mountpoint rename/symlink swaps, unsafe options, `allow_other` gating, `mount_max`, option strings longer than page size, `x-` mtab options, `auto_unmount`, sync-init success/failure, fd-passing failure, unmount ownership checks, and namespace-based mount validation.
