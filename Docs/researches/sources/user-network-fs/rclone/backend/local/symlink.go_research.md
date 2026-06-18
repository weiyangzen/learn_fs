
# sources/user-network-fs/rclone/backend/local/symlink.go

## Purpose
Detects circular symlink errors on Unix-like platforms.

## Important APIs, Types, And Control Flow
`isCircularSymlinkError` unwraps `*os.PathError`, checks for a `syscall.Errno`, and returns true when the errno is `ELOOP`.

## State And Persistence
No state is modified.

## Dependencies And Integration Points
Used in local `List` when following symlinks to convert circular symlinks into non-retry listing errors instead of aborting traversal.

## Risks And Test Signals
Risks are error wrapping shapes that hide `ELOOP`. Tests should include circular symlink listing in `--copy-links` mode.
