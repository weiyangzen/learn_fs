# sources/sync-backup/syncthing/lib/fs/basicfs_watch_errors_linux.go

## Purpose
Classifies Linux notify setup errors that indicate exhausted inotify watch limits, enabling a user-facing remediation message.

## Important APIs, Types, and Functions
`reachedMaxUserWatches(err error) bool` unwraps `*os.PathError`, then checks `syscall.Errno` for `24` and `28`.

## Control Flow
Called from `BasicFilesystem.Watch` when `notify.WatchWithFilter` fails. A recognized error is replaced with a Syncthing FAQ message about increasing inotify limits.

## State and Persistence Behavior
No state or persistence.

## Dependencies and Integration Points
Linux-only build. Coupled to notify/inotify behavior and `basicfs_watch.go` error reporting.

## Risks
The errno checks are numeric and intentionally broad: `EMFILE` and `ENOSPC` can have meanings outside inotify in other contexts, but here they occur during watch setup.

## Test Signals
`TestWatchErrorLinuxInterpretation` validates errno 24 and 28 are recognized and ordinary errors are not.
