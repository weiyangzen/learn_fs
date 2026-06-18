
# sources/user-network-fs/rclone/backend/local/metadata.go

## Purpose
Defines local backend metadata keys and shared metadata parsing/writing behavior.

## Important APIs, Types, And Control Flow
`systemMetadataInfo` documents owned keys: mode, uid, gid, rdev, atime, mtime, and btime. `parseMetadataTime` and `parseMetadataInt` parse RFC3339Nano and integer values with debug logging on invalid input. `writeMetadataToFile` applies atime/mtime, optional btime, ownership, and mode. It uses no-follow helpers for translated symlinks and regular OS calls for normal files.

## State And Persistence
Persists filesystem timestamps, ownership, and permissions. Does not currently write `rdev`.

## Dependencies And Integration Points
Relies on OS-specific `readMetadataFromFile`, `readTime`, `lChtimes`, `lChmod`, and btime helpers. Called by object and directory metadata setters.

## Risks And Test Signals
Risks include partial metadata application, privilege failures on ownership, symlink-target safety, Windows/Plan9 ownership no-op, mode parsing limits, and unsupported birth time. Tests should verify invalid metadata is ignored/logged and that symlink writes do not alter targets.
