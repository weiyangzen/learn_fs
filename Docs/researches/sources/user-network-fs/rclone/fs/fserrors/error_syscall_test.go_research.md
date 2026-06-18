<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fserrors/error_syscall_test.go -->
# sources/user-network-fs/rclone/fs/fserrors/error_syscall_test.go

## Purpose
Tests retry and cause behavior for wrapped syscall/network errors.

## Important APIs, Types, And Control Flow
`makeNetErr` constructs a `net.OpError` around a `os.SyscallError`. Tests assert `Cause` reaches the syscall errno and `ShouldRetry` returns true for retriable syscall causes.

## State And Persistence
No persistence; local error values only.

## Dependencies And Integration Points
Uses platform syscall constants through the current build and the fserrors classifier.

## Risks And Test Signals
Coverage depends on platform-specific errno availability. Windows-specific extra codes are covered by build-specific initialization rather than this table alone.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fserrors/error_syscall_test.go -->
