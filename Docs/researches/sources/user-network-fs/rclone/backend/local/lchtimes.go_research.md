
# sources/user-network-fs/rclone/backend/local/lchtimes.go

## Purpose
Provides a no-op link timestamp setter on Plan 9 and JS.

## Important APIs, Types, And Control Flow
Sets `haveLChtimes = false` and implements `lChtimes` to return nil without changing atime or mtime.

## State And Persistence
No metadata is persisted for symlink times.

## Dependencies And Integration Points
Called by `Object.setTimes` when an object is a translated symlink.

## Risks And Test Signals
The no-op prevents unsupported platform failures but hides inability to set link times. Tests should account for `haveLChtimes` before expecting symlink time round trips.
