
# sources/user-network-fs/rclone/backend/local/setbtime.go

## Purpose
Provides non-Windows stubs for setting birth/creation time.

## Important APIs, Types, And Control Flow
Sets `haveSetBTime = false`; `setBTime` and `lsetBTime` return nil without changes.

## State And Persistence
No birth time metadata is written.

## Dependencies And Integration Points
Used by shared metadata write code, which checks `haveSetBTime` before attempting btime writes.

## Risks And Test Signals
Silent no-op is guarded by capability flag. Tests should skip btime write expectations when `haveSetBTime` is false.
