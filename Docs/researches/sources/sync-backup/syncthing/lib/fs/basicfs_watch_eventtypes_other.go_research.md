# sources/sync-backup/syncthing/lib/fs/basicfs_watch_eventtypes_other.go

## Purpose
Provides a fallback notify event mask for platforms not otherwise covered.

## Important APIs, Types, and Functions
`subEventMask = notify.All`, `permEventMask = 0`, and `rmEventMask = notify.Remove | notify.Rename`.

## Control Flow
Generic watcher subscribes to all notify events, then collapses remove/rename to `Remove` and everything else to `NonRemove`.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Catch-all build selection for non-Linux, non-Windows, non-BSD, non-Solaris, non-Darwin, non-cgo, non-iOS platforms.

## Risks
Subscribing to all events can create extra scan wakeups. Platform notify support may still be incomplete even when this compiles.

## Test Signals
No direct tests for this catch-all path; behavioral validation depends on platform-specific test runs.
