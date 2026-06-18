# sources/user-network-fs/rclone/vfs/vfstest/dir.go

## Purpose
Contains functional directory tests shared by direct VFS and mounted filesystem runs.

## APIs, Flow, And State
Tests cover directory listing, creating/removing empty and non-empty directories, file creation/removal inside directories, file rename, empty directory rename, full directory rename, directory modtime, explicit directory-cache flush, and cache flush on directory rename. They use the global `run` harness to create local operations, inspect local and remote trees, and call `forget`.

## Dependencies And Integration
Depends on `vfstest.Run`, remote `Mkdir`, and `Run.checkDir`, which compares FUSE/VFS view against remote listing with retry for eventual consistency.

## Risks And Test Signals
These tests detect stale directory caches, missing rename propagation, permission drift, and incorrect non-empty directory removal. They are skipped when FUSE/direct prerequisites are unavailable through harness checks.
