<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fs.go -->
# sources/user-network-fs/rclone/fs/fs.go

## Purpose
Defines core filesystem constants, common errors, a multipart minimum-size error type, and small utility helpers.

## Important APIs, Types, And Control Flow
Constants include unsupported modtime precision, infinite listing level, and symlink suffix. Exported errors cover config lookup, copy/move/purge capability failures, listing/object/directory conditions, deletion safeguards, immutability, permission, not-implemented, command, filename, root listing, and multipart size. `FileTooSmallError` wraps `ErrorFileTooSmall`. `CheckClose` preserves close errors only when no prior error exists. `FileExists` calls `NewObject` and maps not-found/not-file/permission to false. `GetModifyWindow` returns the max of config modify window and all Fs precisions, short-circuiting unsupported modtime.

## State And Persistence
No persistent state. `GetModifyWindow` reads context config.

## Dependencies And Integration Points
These errors and helpers are used throughout backends and operations as common contracts.

## Risks And Test Signals
Error identity comparisons matter. `FileExists` treating permission denied as non-existence is a deliberate semantic choice. Tests in this subset focus on `Features`, not these helpers directly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fs.go -->
