# sources/sync-backup/syncthing/lib/fs/basicfs_watch_notkqueue.go

## Purpose
Provides `WatchKqueue = false` for non-kqueue platforms.

## Important APIs, Types, and Functions
Single constant `WatchKqueue`.

## Control Flow
No control flow; compile-time platform signal.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Complements `basicfs_watch_eventtypes_kqueue.go` so callers can use `WatchKqueue` on all builds.

## Risks
The build tags must remain the exact inverse of kqueue-supported tags to avoid duplicate or missing constants.

## Test Signals
No direct tests; compilation across build matrix is the primary signal.
