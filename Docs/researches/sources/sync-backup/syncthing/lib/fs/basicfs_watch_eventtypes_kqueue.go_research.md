# sources/sync-backup/syncthing/lib/fs/basicfs_watch_eventtypes_kqueue.go

## Purpose
Defines notify masks for kqueue-style platforms and exposes whether kqueue watching is selected.

## Important APIs, Types, and Functions
`subEventMask` includes delete, write, rename, synthetic create, attrib, and extend. `permEventMask` is zero. `rmEventMask` covers delete and rename. `WatchKqueue = true`.

## Control Flow
The generic watcher subscribes to these masks where the supported watch implementation is compiled. The `WatchKqueue` constant lets other code distinguish kqueue behavior.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Builds for BSDs, iOS, or explicit `kqueue`. Uses `github.com/syncthing/notify`.

## Risks
kqueue lacks native create events, relying on notify synthesis; this may differ from inotify/FSEvents behavior. Some darwin+kqueue combinations use the unsupported watcher file instead.

## Test Signals
Watch tests have platform skips and expectations, but full validation requires target OS coverage.
