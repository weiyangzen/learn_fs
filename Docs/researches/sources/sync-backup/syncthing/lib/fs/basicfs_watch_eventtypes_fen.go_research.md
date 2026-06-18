# sources/sync-backup/syncthing/lib/fs/basicfs_watch_eventtypes_fen.go

## Purpose
Defines Solaris FEN notify masks for cgo builds.

## Important APIs, Types, and Functions
Constants select `notify.Create`, file modified/delete/rename events, no-follow behavior, `FileAttrib` permissions, and remove masks for delete or rename-from.

## Control Flow
The masks are consumed by the generic `BasicFilesystem.Watch` setup and `eventType` mapping.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Builds only for `solaris && cgo`. Integrates with `github.com/syncthing/notify`.

## Risks
Solaris event naming distinguishes rename-from and rename-to; only rename-from is remove-like. Incorrect mask composition can produce duplicate or missing scan triggers.

## Test Signals
Watcher tests include Solaris in platform conditionals for rename expectations, but full coverage depends on running on Solaris with cgo.
