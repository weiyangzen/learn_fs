
# sources/user-network-fs/rclone/backend/local/metadata_linux.go

## Purpose
Implements Linux metadata reads, preferring `statx` when available and falling back to `fstatat`.

## Important APIs, Types, And Control Flow
`readTime` supports atime and ctime from `syscall.Stat_t`. `readMetadataFromFile` initializes a once-selected reader: `readMetadataFromFileStatx` if `statx` is available and not Android, otherwise `readMetadataFromFileFstatat`. The statx path reads type, mode, uid, gid, atime, mtime, ctime, and btime; the fallback reads mode, uid, gid, rdev, atime, and mtime.

## State And Persistence
No writes; caches the chosen metadata read function in package globals.

## Dependencies And Integration Points
Uses `golang.org/x/sys/unix`, local `FollowSymlinks` to choose no-follow flags, and supplies local metadata/time-type behavior.

## Risks And Test Signals
Risks include kernel `statx` availability detection, Android exclusion, architecture-dependent timespec casts, symlink no-follow correctness, and btime absence in fallback. Tests should exercise both statx and fallback where possible.
