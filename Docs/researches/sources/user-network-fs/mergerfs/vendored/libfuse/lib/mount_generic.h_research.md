# sources/user-network-fs/mergerfs/vendored/libfuse/lib/mount_generic.h

## Purpose
`mount_generic.h` implements Linux/Unix-generic FUSE mount and unmount logic, including direct kernel `mount(2)` and fallback to `fusermount`/`fusermount3`.

## Important APIs, Types, and Functions
Exports are `fuse_kern_mount` and `fuse_kern_unmount`. Internal pieces include `mount_opts`, `fuse_mount_opts`, `exec_fusermount`, `set_mount_flag`, `fuse_mount_opt_proc`, `receive_fd`, `fuse_mount_sys`, `fuse_mount_fusermount`, and `get_mnt_flag_opts`.

## Control Flow
Arguments are parsed into kernel flags, kernel options, fusermount-only options, subtype options, and mtab options. `fuse_mount_sys` validates/repairs a mountpoint, opens `/dev/fuse`, appends fd/rootmode/user/group options, builds the FUSE type/source, and attempts `mount(2)`. EPERM or `auto_unmount` triggers fallback to `fuse_mount_fusermount`, which forks a helper, passes a communication fd in `_FUSE_COMMFD`, and receives the mounted fuse fd via `SCM_RIGHTS`. Unmount closes the fd, checks for already-unmounted poll errors, uses direct lazy unmount as root, or execs fusermount for unprivileged users.

## State and Persistence
The implementation mutates the OS mount table, `/etc/mtab` through `mount_util.h` when appropriate, child process state, and open fds. Parsed strings are freed before return.

## Dependencies and Integration Points
It depends on `fuse_opt`, `mount_util.h`, POSIX sockets/fork/mount APIs, and `fusermount` binaries. `helper.cpp` calls it through `fuse_mount_common` and teardown.

## Risks
Mount security and fd passing are sensitive. The fixed argv array limits option count. Direct mount fallback decisions rely on errno. `auto_unmount` only works through helper mode. `receive_fd` validates only basic control-message shape.

## Test Signals
Test direct root mount, unprivileged fusermount fallback, `auto_unmount`, subtype and fsname combinations, `fuseblk` missing support, broken mountpoint ENOTCONN recovery, mtab updates, fd close behavior, and helper exec failure paths.
