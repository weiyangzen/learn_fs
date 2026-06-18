# sources/sync-backup/syncthing/lib/fs/basicfs_watch.go

## Purpose
Implements recursive file watching for `BasicFilesystem` using `github.com/syncthing/notify`, normalizing backend events into Syncthing `fs.Event` values.

## Important APIs, Types, and Functions
`backendBuffer` sizes the notify channel. `Watch` prepares paths and masks, installs `notify.WatchWithFilter`, handles inotify limit errors, and starts `watchLoop`. `watchLoop` drains overflow, validates UTF-8, converts absolute paths to relative names, applies ignore rules, sends events and fatal errors, and stops notify on context cancellation. `eventType` maps remove masks to `Remove`, everything else to `NonRemove`.

## Control Flow
Setup calls platform `watchPaths`, constructs event masks from `subEventMask` and optional `permEventMask`, and passes a filter that drops invalid or ignorable absolute paths. Runtime loop first detects full backend buffer and emits a broad rescan event for the watched root, then processes backend events or context cancellation.

## State and Persistence Behavior
No persistent state. Runtime state is channels, notify backend registration, and context lifetime. Overflow intentionally coalesces lost events into a root-level non-remove event.

## Dependencies and Integration Points
Depends on platform event mask files, `unrootedChecked`, `Matcher.Match`, and `ignoreresult` semantics. Integrated through `Filesystem.Watch`.

## Risks
Incorrect platform masks can miss changes or misclassify renames. Fatal outside-root events stop the watcher. Overflow uses `len(channel) == backendBuffer`, which is a heuristic sensitive to backend scheduling. Invalid UTF-8 paths are silently ignored.

## Test Signals
`basicfs_watch_test.go` covers ignores, includes, rename semantics, overflow, outside-root errors, symlinked roots, subpath watches, modtime changes, and Linux inotify-limit interpretation.
