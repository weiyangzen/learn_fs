
# sources/user-network-fs/rclone/backend/local/metadata_windows.go

## Purpose
Provides Windows metadata reads and time selection.

## Important APIs, Types, And Control Flow
`readTime` reads access time or creation time from `syscall.Win32FileAttributeData`, otherwise mtime. `readMetadataFromFile` sets portable mode plus atime, mtime, and btime from Windows filetime values.

## State And Persistence
Reads metadata only; write support for timestamps is in `setbtime_windows.go`.

## Dependencies And Integration Points
Supports local backend metadata reads and `time_type` on Windows.

## Risks And Test Signals
Risks include missing Windows attribute metadata and filetime conversion precision. Tests should validate creation-time round trips and behavior for reparse points.
