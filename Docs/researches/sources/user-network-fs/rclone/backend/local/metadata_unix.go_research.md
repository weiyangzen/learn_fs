
# sources/user-network-fs/rclone/backend/local/metadata_unix.go

## Purpose
Implements metadata reads for OpenBSD and Solaris.

## Important APIs, Types, And Control Flow
`readTime` extracts atime or ctime from `syscall.Stat_t`, otherwise mtime. `readMetadataFromFile` sets mode, uid, gid, optional rdev, atime, and mtime.

## State And Persistence
Only reads filesystem metadata.

## Dependencies And Integration Points
Feeds local metadata and `time_type` support for OpenBSD/Solaris builds.

## Risks And Test Signals
Risks include missing btime support and `Stat_t` layout differences. Tests should validate supported keys and graceful fallback on unexpected `Sys` values.
