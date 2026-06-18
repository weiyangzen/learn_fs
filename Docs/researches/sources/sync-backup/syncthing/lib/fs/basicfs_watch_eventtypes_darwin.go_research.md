# sources/sync-backup/syncthing/lib/fs/basicfs_watch_eventtypes_darwin.go

## Purpose
Defines notify event masks for Darwin FSEvents builds using cgo and not kqueue/iOS.

## Important APIs, Types, and Functions
Constants: `subEventMask`, `permEventMask`, and `rmEventMask`. The subscription includes create, remove, write, rename, inode metadata, and xattr changes. Owner changes are treated as permission events.

## Control Flow
`basicfs_watch.go` combines `subEventMask` with `permEventMask` unless `ignorePerms` is true. Events matching `rmEventMask` become `Remove`; the rest become `NonRemove`.

## State and Persistence Behavior
No runtime state in this file.

## Dependencies and Integration Points
Darwin-specific build for the notify backend. The inode metadata mask is important for truncate-only and mtime changes.

## Risks
FSEvents can emit parent-directory events or coarse events, so scanner behavior must tolerate extra allowed events. Missing metadata masks would lose changes that do not look like writes.

## Test Signals
`TestWatchModTime` and `TestTruncateFileOnly` document Darwin-specific metadata behavior and allowed parent events.
