# sources/user-network-fs/rclone/vfs/vfstest/edge_cases.go

## Purpose
Holds regression tests for racy VFS/mount edge cases.

## APIs, Flow, And State
`TestTouchAndDelete` creates a zero-byte file and immediately removes it, verifying the tree returns empty. `TestRenameOpenHandle` writes and syncs through an open writer, renames the still-open file, closes it, waits for writers, and verifies the renamed object exists.

## Dependencies And Integration
Uses write helpers from `file.go`, `run.waitForWriters`, and shared directory comparison. Windows skips the open-handle rename case.

## Risks And Test Signals
Targets known race patterns: zero-byte create/delete and renaming before writer close. Failures indicate delayed writeback or directory-cache sequencing issues.
