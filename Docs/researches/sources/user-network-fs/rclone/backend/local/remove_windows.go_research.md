
# sources/user-network-fs/rclone/backend/local/remove_windows.go

## Purpose
Implements Windows removal with retry for sharing violations.

## Important APIs, Types, And Control Flow
`remove` tries `os.Remove` up to ten times. If the error is an `os.PathError` wrapping `windows.ERROR_SHARING_VIOLATION`, it logs, sleeps with exponential backoff starting at 1 ms, and retries.

## State And Persistence
Deletes a filesystem entry after temporary sharing conflicts clear.

## Dependencies And Integration Points
Used by local `Object.Remove` and cleanup paths on Windows. Integrates with fs logging and `x/sys/windows` errno constants.

## Risks And Test Signals
Risks include insufficient retry budget or masking non-sharing errors. `remove_test.go` is the direct signal for open-file deletion behavior.
