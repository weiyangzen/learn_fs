<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fserrors/enospc_error.go -->
# sources/user-network-fs/rclone/fs/fserrors/enospc_error.go

## Purpose
Non-Plan9 implementation for detecting disk-full errors in wrapped error chains.

## Important APIs, Types, And Control Flow
`IsErrNoSpace` walks an error chain with `lib/errors.Walk` and returns true if any cause equals `syscall.ENOSPC`.

## State And Persistence
Pure error inspection with no state.

## Dependencies And Integration Points
Used by operations that need to classify no-space failures specially. Depends on syscall `ENOSPC` and rclone error walking.

## Risks And Test Signals
Only exact `syscall.ENOSPC` is detected; string-only errors are not. Plan9 has a separate false implementation. Tests for wrapped syscall causes cover this area indirectly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fserrors/enospc_error.go -->
