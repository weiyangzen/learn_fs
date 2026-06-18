# sources/user-network-fs/bazil-fuse/unmount_std.go

Purpose: This non-Linux implementation unmounts using the Go `syscall.Unmount` API.

Important APIs, types, and functions: `unmount(dir string) error` calls `syscall.Unmount(dir, 0)` and wraps failures in `*os.PathError{Op: "unmount", Path: dir, Err: err}`.

Control flow: Single syscall with error wrapping on failure.

State and persistence behavior: No internal state. It changes the OS mount table.

Dependencies and integration points: Built when `!linux`; used by public `Unmount`, including FreeBSD builds.

Risks: Does not use a platform helper, so behavior depends directly on syscall permissions and platform semantics. No forced/lazy unmount flags are used.

Test signals: FreeBSD integration cleanup paths indirectly exercise it.
