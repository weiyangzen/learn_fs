# sources/user-network-fs/go-fuse/fs/loopback_freebsd.go

Purpose: FreeBSD-specific loopback helpers for timestamps, copy-file-range, device conversion, and xattr listing format conversion.

Important functions: `doCopyFileRange` manually invokes syscall 569; `intDev` returns `uint64`; `rebuildAttrBuf` prefixes FreeBSD xattr names with `user.` and null-terminates them; `LoopbackNode.Listxattr` calls `unix.Llistxattr`, parses names, rebuilds Linux-flavored listxattr output, and copies into dest when provided.

State/dependencies: no persistent state beyond backing filesystem xattrs.

Integration/risks: bridges FreeBSD syscall behavior to Linux FUSE expectations. Risks include syscall constant drift, namespace mapping assumptions, truncated-copy semantics, and platform differences in xattr permissions. FreeBSD cross-build covers compilation; runtime tests would be needed for xattr behavior.
