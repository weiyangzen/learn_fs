# sources/user-network-fs/rclone/cmd/selfupdate/writable_unix.go

## Purpose

This platform implementation decides whether a path is writable on non-Windows, non-Plan9, non-JS self-update builds.

## Important APIs, Types, and Functions

`writable(path string) bool` calls `unix.Access(path, unix.W_OK)` and returns true only when the kernel reports write access.

## Control Flow

There is no branching beyond the syscall result. The caller can use this as a preflight for replacing the current executable or related files.

## State and Persistence Behavior

No state is stored. The result is a point-in-time permissions check and can race with later chmod, ownership, mount, or ACL changes.

## Dependencies and Integration Points

It depends on `golang.org/x/sys/unix` and is selected by `!windows && !plan9 && !js && !noselfupdate`. It integrates with the self-update install path checks.

## Risks and Test Signals

`access(2)` can be misleading under elevated effective IDs or unusual ACL/security module policy, and any check-then-write sequence is inherently racy. No direct tests in this subset exercise platform-specific permission behavior.
