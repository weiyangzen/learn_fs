
# sources/user-network-fs/rclone/backend/local/read_device_unix.go

## Purpose
Reads filesystem device IDs for Unix-like platforms that support `syscall.Stat_t.Dev`.

## Important APIs, Types, And Control Flow
`readDevice` returns `devUnset` unless `oneFileSystem` is true. When enabled, it asserts `fi.Sys().(*syscall.Stat_t)` and returns `Dev`; assertion failures are logged and treated as unset.

## State And Persistence
Reads file metadata only. The returned value is stored in `Fs.dev` and compared during listing.

## Dependencies And Integration Points
Supports local backend `--one-file-system` by preventing directory traversal across device boundaries.

## Risks And Test Signals
Risks include type assertion failures on unusual filesystems and platform-specific device IDs. Tests should create or mock different devices if possible and verify boundary filtering.
