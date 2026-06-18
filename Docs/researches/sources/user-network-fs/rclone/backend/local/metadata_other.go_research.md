
# sources/user-network-fs/rclone/backend/local/metadata_other.go

## Purpose
Provides minimal metadata support for DragonFly, Plan 9, JS, and AIX.

## Important APIs, Types, And Control Flow
`readTime` always returns `fi.ModTime`. `readMetadataFromFile` reads local info and sets only `mode` and `mtime`.

## State And Persistence
Reads metadata only; no persistent changes.

## Dependencies And Integration Points
Acts as the build-tag fallback for platforms without richer stat support.

## Risks And Test Signals
Capabilities are intentionally limited. Tests should expect absent uid/gid/atime/btime/ctime and confirm no crashes on unsupported platforms.
