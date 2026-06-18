
# sources/user-network-fs/rclone/backend/local/lchtimes_unix.go

## Purpose
Implements no-follow symlink timestamp updates on Unix-like platforms except Windows, Plan 9, and JS.

## Important APIs, Types, And Control Flow
`lChtimes` converts access and modification times to `unix.Timespec` values and calls `unix.UtimesNanoAt` with `AT_SYMLINK_NOFOLLOW`.

## State And Persistence
Persists link atime and mtime without touching the target where the OS supports it.

## Dependencies And Integration Points
Supports local backend `--links` mode, metadata writes, and symlink tests that check `haveLChtimes`.

## Risks And Test Signals
Risks are filesystem support differences and precision rounding. Tests should compare times within filesystem precision and verify target metadata is not modified.
