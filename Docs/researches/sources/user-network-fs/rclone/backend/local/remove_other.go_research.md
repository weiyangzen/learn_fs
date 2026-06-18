
# sources/user-network-fs/rclone/backend/local/remove_other.go

## Purpose
Defines normal local object removal on non-Windows platforms.

## Important APIs, Types, And Control Flow
`remove` simply calls `os.Remove(name)`.

## State And Persistence
Deletes the named filesystem entry if allowed by the OS.

## Dependencies And Integration Points
Called by `Object.Remove` and partial-write cleanup paths.

## Risks And Test Signals
Behavior is OS-native. Tests should verify error propagation and successful deletion of normal files; open-file deletion behavior differs from Windows.
