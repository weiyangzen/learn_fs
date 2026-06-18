# sources/user-network-fs/bazil-fuse/options_freebsd.go

Purpose: This FreeBSD-specific file implements `DaemonTimeout` support.

Important APIs, types, and functions: `daemonTimeout(name string) MountOption` returns an option that sets `conf.options["timeout"] = name`.

Control flow: The returned closure mutates the mount config when `Mount` applies options.

State and persistence behavior: Transient mount configuration only.

Dependencies and integration points: Used by the public `DaemonTimeout` function in `options.go`; consumed by `mount_freebsd.go` through `conf.getOptions`.

Risks: The value is a raw string, so validation is delegated to the FreeBSD mount helper. FreeBSD option serialization cannot tolerate commas.

Test signals: No direct test in this subset validates `DaemonTimeout`; FreeBSD option behavior is otherwise covered indirectly by mount option tests with platform skips.
