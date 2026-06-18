# sources/sync-backup/syncthing/lib/fs/basicfs_watch_eventtypes_inotify.go

## Purpose
Defines Linux inotify masks used by `BasicFilesystem.Watch`.

## Important APIs, Types, and Functions
`subEventMask` includes create, moved-to, delete, delete-self, modify, moved-from, move-self, and attrib events. `permEventMask` is zero because `InAttrib` is always subscribed to catch both permissions and modtime. `rmEventMask` covers delete and moved-from/self removal events.

## Control Flow
All Linux watches include attrib notifications regardless of `ignorePerms`; `eventType` maps delete/move-away to `Remove`.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Linux-only notify integration for scanner invalidation and permission/modtime detection.

## Risks
`ignorePerms` cannot suppress `InAttrib` because it is also needed for modtime, so permission-only changes may still wake scans on Linux.

## Test Signals
Watcher tests exercise rename, modtime, modify, overflow, and Linux inotify-limit error handling.
