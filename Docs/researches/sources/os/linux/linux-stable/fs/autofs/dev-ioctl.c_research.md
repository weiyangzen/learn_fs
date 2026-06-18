# File Research: sources/os/linux/linux-stable/fs/autofs/dev-ioctl.c

## Purpose
Implements the `/dev/autofs` miscellaneous-device ioctl interface, allowing userspace daemons and tools to control autofs mounts even when mountpoints are covered by other mounts.

## Main Interfaces
Supports device ioctl commands for interface/protocol version, open/close mount fd, ready/fail wait completion, set pipe fd, catatonic mode, timeout management, requester uid/gid lookup, expire, ask-umount, and mountpoint checks.

## Important Behavior
The dispatcher copies a variable-sized `struct autofs_dev_ioctl` from userspace, validates version and path encoding, checks command range, gates most commands behind `CAP_SYS_ADMIN`, resolves an optional autofs mount fd, checks owner-daemon mode, and dispatches through a fixed function table with `array_index_nospec()`.

`openmount` finds the topmost autofs mount matching a path and device id and returns an O_CLOEXEC fd. `setpipefd` reconnects a catatonic mount to a new daemon pipe only within the same pid namespace. `timeout` supports both superblock-wide and per-dentry indirect mount timeouts. `ismountpoint` can operate with or without an autofs fd and returns mount status, device, and covering filesystem magic.

## Cross-File Relationships
Calls `autofs_wait_release()`, `autofs_catatonic_mode()`, `autofs_expire_wait()`, and `autofs_do_expire_multi()`. Relies on autofs mount type helpers, VFS path lookup/mount traversal, and miscdevice registration.

## Risks / Review Notes
The ioctl struct has embedded path data, so size and NUL-termination validation are security-sensitive. Reconnecting daemon pipes requires careful namespace and catatonic-state checks. Some commands intentionally work without an existing autofs fd, which makes path lookup behavior part of the ABI.
