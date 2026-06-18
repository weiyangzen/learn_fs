
# sources/user-network-fs/rclone/backend/local/lchmod_unix.go

## Purpose
Provides symlink chmod support on Unix platforms where `fchmodat` with `AT_SYMLINK_NOFOLLOW` works.

## Important APIs, Types, And Control Flow
`syscallMode` maps Go mode bits to syscall permission, setuid, setgid, and sticky bits. `lChmod` calls `unix.Fchmodat` with `AT_SYMLINK_NOFOLLOW` and wraps failures in `os.PathError`.

## State And Persistence
Persists mode changes on the link itself, not the target, on supported platforms.

## Dependencies And Integration Points
Used by `writeMetadataToFile` for translated symlink `mode` metadata. Linux is excluded because its `fchmodat` behavior does not support this flag safely.

## Risks And Test Signals
Risks include platform kernel differences and incorrect mode bit mapping. Tests should verify target permissions remain unchanged and link mode errors are surfaced.
