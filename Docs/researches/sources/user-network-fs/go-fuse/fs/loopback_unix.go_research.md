# sources/user-network-fs/go-fuse/fs/loopback_unix.go

Purpose: non-FreeBSD loopback xattr-list implementation.

Important API: `LoopbackNode.Listxattr` calls `unix.Llistxattr(n.path(), dest)` and returns size/error converted to `syscall.Errno`.

Control flow/state: no retained state; delegates to backing filesystem.

Dependencies/integration: build-tagged `!freebsd`, used on Linux/Darwin where Linux-style listxattr data is acceptable to the rest of the stack. Risks are platform differences under the broad build tag, especially Darwin xattr format expectations. Tests cover Linux symlink xattr behavior; additional platform-specific runtime tests would help.
