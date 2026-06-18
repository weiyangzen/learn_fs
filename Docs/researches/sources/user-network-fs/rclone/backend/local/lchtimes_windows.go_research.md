
# sources/user-network-fs/rclone/backend/local/lchtimes_windows.go

## Purpose
Implements symlink timestamp updates on Windows.

## Important APIs, Types, And Control Flow
Sets `haveLChtimes = true` and delegates `lChtimes` to `setTimes` with the `link` flag enabled and no birth-time change.

## State And Persistence
Persists atime and mtime on the reparse point rather than the target.

## Dependencies And Integration Points
Uses the Windows `setbtime_windows.go` helper and is called from translated symlink metadata paths.

## Risks And Test Signals
Risks include Windows handle flags and privilege/attribute behavior. Tests should verify link-target isolation and timestamp round trips on Windows.
