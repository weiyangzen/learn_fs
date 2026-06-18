
# sources/user-network-fs/rclone/backend/local/metadata_bsd.go

## Purpose
Implements metadata reads and selectable times for Darwin, FreeBSD, and NetBSD.

## Important APIs, Types, And Control Flow
`readTime` extracts atime, birth time, or ctime from `syscall.Stat_t`, falling back to mtime. `readMetadataFromFile` lstat/stat reads mode, uid, gid, rdev, atime, mtime, and btime into `fs.Metadata`.

## State And Persistence
Only reads filesystem metadata; writes are handled by shared metadata code.

## Dependencies And Integration Points
Uses BSD `Stat_t` `Timespec` fields and feeds local `Object.Metadata` and configured `time_type`.

## Risks And Test Signals
Risks include failed `Sys` type assertions and platform-specific nanosecond precision. Tests should verify btime/ctime/atime exposure on supported BSD systems and symlink behavior.
