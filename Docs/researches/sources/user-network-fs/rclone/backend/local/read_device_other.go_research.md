
# sources/user-network-fs/rclone/backend/local/read_device_other.go

## Purpose
Provides a device-ID fallback for platforms without supported stat device fields.

## Important APIs, Types, And Control Flow
`readDevice` ignores its inputs and returns `devUnset`.

## State And Persistence
No state is read or modified beyond receiving an `os.FileInfo`.

## Dependencies And Integration Points
Used by local `NewFs` and `List` for `--one-file-system`; on these platforms that feature cannot enforce boundaries.

## Risks And Test Signals
Risk is user expectation mismatch for `--one-file-system`. Tests should confirm device filtering is effectively disabled on unsupported platforms.
