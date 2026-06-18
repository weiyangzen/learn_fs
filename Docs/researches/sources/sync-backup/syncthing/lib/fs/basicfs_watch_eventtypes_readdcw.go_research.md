# sources/sync-backup/syncthing/lib/fs/basicfs_watch_eventtypes_readdcw.go

## Purpose
Defines Windows ReadDirectoryChangesW notify masks.

## Important APIs, Types, and Functions
`subEventMask` includes file and directory name changes, size, creation, and last-write changes. `permEventMask` is attributes. `rmEventMask` covers removed and renamed-old-name actions.

## Control Flow
Used by the generic watcher to configure notify subscriptions and classify backend remove events.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Windows-only build. Interacts with Windows path normalization and 8.3 name handling in `basicfs_windows.go`.

## Risks
Windows watcher events can vary by case, short names, and root spelling. Attribute-only notifications are suppressed only when `ignorePerms` omits `permEventMask`.

## Test Signals
`basicfs_watch_test.go` includes Windows-specific root, case, and issue-regression scenarios.
