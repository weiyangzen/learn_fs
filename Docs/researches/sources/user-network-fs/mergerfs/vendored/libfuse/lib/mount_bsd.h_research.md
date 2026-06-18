# sources/user-network-fs/mergerfs/vendored/libfuse/lib/mount_bsd.h

## Purpose
`mount_bsd.h` implements kernel mount and unmount support for BSD-style FUSE environments using `mount_fusefs`.

## Important APIs, Types, and Functions
It defines BSD mount option parsing via `fuse_mount_opts`, `mount_opts`, `fuse_mount_opt_proc`, `fuse_kern_mount`, and `fuse_kern_unmount`. Helpers include `mount_help`, `mount_version`, `do_unmount`, `init_backgrounded`, and `fuse_mount_core`.

## Control Flow
`fuse_kern_mount` sets environment markers for `mount_fusefs`, parses args into kernel options, handles help/version, then calls `fuse_mount_core`. Core accepts an inherited `FUSE_DEV_FD`, opens a fuse device from `FUSE_DEV_NAME` or `/dev/fuse`, optionally forks and execs `mount_fusefs` with fd and mountpoint, and returns the device fd. Unmount resolves the fuse character device from `fstat`, validates it looks like a fuse device, forks `/sbin/umount -f`, then closes the fd.

## State and Persistence
It manipulates process environment, open fds, child processes, and the OS mount table. No library heap state persists except parsed option strings during the call.

## Dependencies and Integration Points
The file depends on BSD headers, `fuse_opt`, and `mount_fusefs`. It is selected by `mount.hpp` for BSD platforms and called by `helper.cpp`.

## Risks
The argv array for `mount_fusefs` is fixed size. Environment variables can redirect fd/device behavior. Fork/wait error handling is minimal. Unmount depends on BSD device naming and may no-op if validation fails.

## Test Signals
BSD tests should cover inherited `FUSE_DEV_FD`, device open, `FUSE_NO_MOUNT`, help/version options, kernel option forwarding, init-backgrounded behavior, mount helper failure, and unmount of valid/invalid fuse fds.
