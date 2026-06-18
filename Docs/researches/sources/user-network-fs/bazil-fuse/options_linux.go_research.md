# sources/user-network-fs/bazil-fuse/options_linux.go

Purpose: This Linux-specific file defines `DaemonTimeout` as a no-op because the option is FreeBSD-only.

Important APIs, types, and functions: `daemonTimeout(name string) MountOption` returns `dummyOption`.

Control flow: Applying this option on Linux does nothing and returns nil.

State and persistence behavior: No state changes.

Dependencies and integration points: Used by public `DaemonTimeout` in `options.go` to keep the API portable.

Risks: Callers may assume the timeout is enforced on Linux, but the `options.go` comment says non-FreeBSD platforms ignore it.

Test signals: No direct test in this subset.
