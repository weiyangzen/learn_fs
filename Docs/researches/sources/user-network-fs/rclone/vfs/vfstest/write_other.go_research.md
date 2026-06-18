# sources/user-network-fs/rclone/vfs/vfstest/write_other.go

## Purpose
Provides fallback implementations for write double-close and fd duplication on unsupported non-Unix, non-Windows platforms.

## APIs, Flow, And State
`TestWriteFileDoubleClose` skips with `runtime.GOOS`. `writeTestDup` returns a not-supported error. No persistent state is created.

## Dependencies And Integration
Selected by build tags excluding Unix-like dup support and Windows. It keeps shared write tests buildable.

## Risks And Test Signals
Duplicate-writer behavior is untested on these platforms. The explicit skip/error path avoids false expectations where no fd-dup primitive is available.
