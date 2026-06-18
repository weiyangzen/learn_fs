# sources/user-network-fs/bazil-fuse/unmount.go

Purpose: `unmount.go` exposes the public unmount API.

Important APIs, types, and functions: `Unmount(dir string) error` delegates to the platform-specific private `unmount` implementation.

Control flow: Single direct call.

State and persistence behavior: No internal state. It affects the OS mount table by unmounting a FUSE mount.

Dependencies and integration points: Called by users and by `Mount` cleanup after failed init. The implementation is selected from `unmount_linux.go` or `unmount_std.go`.

Risks: Behavior and error messages are platform-specific. Callers must close active connections or files as needed to avoid busy mounts.

Test signals: Many integration tests defer mount cleanup through `fstestutil`, which ultimately relies on this API.
