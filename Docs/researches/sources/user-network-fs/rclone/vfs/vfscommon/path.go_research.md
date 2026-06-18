# sources/user-network-fs/rclone/vfs/vfscommon/path.go

## Purpose
Provides parent-directory helpers for OS-native paths and rclone slash-separated paths.

## APIs, Flow, And State
`OSFindParent` wraps `filepath.Dir` and normalizes `.` or filesystem root to an empty parent. `FindParent` does the same for slash paths with `path.Dir`. There is no state or persistence.

## Dependencies And Integration
Used by VFS path-resolution code that needs a parent path without leaking Go's `.` or `/` root conventions into rclone logic.

## Risks And Test Signals
Root and platform separator handling are the main risks. The helpers are small and not directly tested in this subset; caller tests around stat/open/rename parent behavior provide indirect coverage.
