
# sources/user-network-fs/rclone/backend/local/symlink_other.go

## Purpose
Provides circular symlink detection for Windows, Plan 9, and JS where Unix `ELOOP` is not used.

## Important APIs, Types, And Control Flow
`isCircularSymlinkError` checks whether the error string contains "The name of the file cannot be resolved by the system".

## State And Persistence
No state is modified.

## Dependencies And Integration Points
Supports local listing behavior when following links on non-Unix platforms.

## Risks And Test Signals
String matching is brittle and locale-sensitive. Windows tests should cover circular/junction resolution errors if feasible.
