
# sources/user-network-fs/rclone/backend/local/local_internal_windows_test.go

## Purpose
Tests Windows-specific directory removal behavior for read-only directories.

## Important APIs, Types, And Control Flow
`TestRmdirWindows` creates a local directory through rclone operations, marks it with `FILE_ATTRIBUTE_DIRECTORY | FILE_ATTRIBUTE_READONLY`, then calls `operations.Rmdir` and expects success.

## State And Persistence
Uses a temporary local test root and modifies Windows file attributes on a test directory.

## Dependencies And Integration Points
Depends on `syscall.SetFileAttributes`, rclone `operations`, and local `Rmdir` fallback that chmods before remove when Windows returns permission errors.

## Risks And Test Signals
Validates a Windows-specific workaround for Go issue 26295. It is skipped outside Windows and does not cover other attributes such as hidden/system.
