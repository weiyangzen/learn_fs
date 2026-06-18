# File Research: sources/os/linux/linux/fs/autofs/dev-ioctl.c

## Summary
Implements `/dev/autofs`, a misc-device ioctl interface for controlling autofs mounts even when their mountpoints are covered by other mounts.

## Main Responsibilities
- Validate and copy `struct autofs_dev_ioctl` requests from userspace.
- Open/close ioctl file descriptors for specific autofs mounts.
- Release wait tokens as ready or failed.
- Reconnect catatonic mounts to a new daemon pipe.
- Put mounts into catatonic mode.
- Set global or per-dentry expire timeouts.
- Query requester uid/gid, protocol versions, expire candidates, umountability, and mountpoint status.

## Key APIs
- `autofs_dev_ioctl_init()`, `autofs_dev_ioctl_exit()`.
- ioctl handlers: version, protover, protosubver, openmount, closemount, ready, fail, setpipefd, catatonic, timeout, requester, expire, askumount, ismountpoint.

## Important Behavior
`copy_dev_ioctl()` copies a variable-sized control structure with an optional path tail, bounded by `PATH_MAX`. `validate_dev_ioctl()` checks interface version, path termination, and command-specific path requirements.

Most commands require `CAP_SYS_ADMIN`; version and ismountpoint are exceptions. Commands that operate on a mount validate the supplied fd points to `autofs_fs_type` and that the caller is oz-mode, except catatonic transition.

`setpipefd` only works when the mount is catatonic and refuses PID namespace changes. It prepares the new FIFO pipe, swaps daemon process group ownership, records the caller’s mount namespace id, and clears catatonic mode.

`ismountpoint` supports both fd-relative checks and path-only checks, returning mountpoint status plus encoded device and superblock magic.

## Risks
This file is a privileged control surface. Correctness depends on strict ioctl version/path validation, `array_index_nospec()` for table dispatch, mount fd type checks, oz-mode enforcement, and careful reconnect semantics for catatonic mounts.
