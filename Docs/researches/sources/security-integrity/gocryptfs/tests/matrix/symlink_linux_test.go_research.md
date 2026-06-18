# sources/security-integrity/gocryptfs/tests/matrix/symlink_linux_test.go

## Purpose
Provides the Linux-specific symlink-open test for matrix mounts, using `openat2` with `O_PATH|O_NOFOLLOW` and `Fstatat(AT_EMPTY_PATH)`.

## Important APIs, Types, And Functions
- `TestOpenSymlinkLinux` creates a dangling symlink, opens the symlink object using `unix.Openat2`, checks target-length size, unlinks it, and attempts a post-unlink empty-path stat.

## Control Flow
The test exercises Linux kernel APIs directly against the FUSE mount to validate symlink dentry metadata and document a known post-unlink compliance limitation.

## State And Persistence
State is a single symlink and an open `O_PATH` fd. The symlink is unlinked before the final stat check.

## Dependencies And Integration Points
Depends on Linux `openat2`, `AT_EMPTY_PATH`, `golang.org/x/sys/unix`, and the shared matrix mount.

## Risks And Edge Cases
The final `Fstatat` failure is logged rather than fatal because gocryptfs is not notified about the earlier `O_PATH` open; treating it as fatal would encode a currently unresolved compliance issue.

## Test Signals
Success is a valid pre-unlink fd stat with correct symlink size and no fatal errors during creation/open/unlink.
