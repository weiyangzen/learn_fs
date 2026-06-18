# sources/user-network-fs/rclone/cmd/selfupdate/writable_windows.go

## Purpose

This Windows implementation estimates whether a path is writable for self-update.

## Important APIs, Types, and Functions

`writable(path string) bool` calls `os.Stat`, checks the permission bits, and treats bit `128` as `UserWritableBit`.

## Control Flow

If `Stat` succeeds, the function returns true when the user-write bit is set. Any stat error returns false.

## State and Persistence Behavior

No state is persisted. The result is a metadata snapshot and can change before update writes.

## Dependencies and Integration Points

The file is selected by `windows && !noselfupdate` and integrates with self-update install checks.

## Risks and Test Signals

Windows ACLs are richer than Go mode bits, so this can produce false positives or negatives on inherited ACLs, UAC elevation, network shares, or read-only attributes. There are no Windows-specific tests in this subset.
