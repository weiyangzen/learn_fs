
# sources/user-network-fs/rclone/backend/local/setbtime_windows.go

## Purpose
Implements Windows atime, mtime, and birth-time updates for files and links.

## Important APIs, Types, And Control Flow
`setTimes` opens the path with `FILE_WRITE_ATTRIBUTES`, `FILE_FLAG_BACKUP_SEMANTICS`, and optionally `FILE_FLAG_OPEN_REPARSE_POINT`, converts non-zero Go times to Windows filetimes, calls `SetFileTime`, and closes the handle. `setBTime` and `lsetBTime` specialize birth-time writes.

## State And Persistence
Persists Windows file timestamps, including creation time and link reparse-point timestamps.

## Dependencies And Integration Points
Shared by `lchtimes_windows.go` and metadata writing. `haveSetBTime = true` enables btime write tests.

## Risks And Test Signals
Risks include handle sharing/permissions, close-error propagation, and link-target confusion. Tests should verify file and symlink timestamp writes on Windows.
