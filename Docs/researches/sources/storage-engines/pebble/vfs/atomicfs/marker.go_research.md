# Research: sources/storage-engines/pebble/vfs/atomicfs/marker.go

## Purpose
`vfs/atomicfs/marker.go` implements an atomic, durable marker abstraction over a filesystem directory. Pebble uses it to point at the current MANIFEST without relying on in-place file overwrite.

## Important APIs, Types, And Functions
Public APIs are `ReadMarker`, `LocateMarker`, `LocateMarkerInListing`, `(*Marker).Move`, `NextIter`, `RemoveObsolete`, `SyncDir`, and `Close`. Marker files are named `marker.<name>.<iter>.<value>` by `markerFilename`, and parsed by `parseMarkerFilename`. `scanForMarker` selects the highest-iteration marker for a marker name and records older files as obsolete.

`Marker` holds the FS, directory, open directory file descriptor, marker name, current filename, current iteration, and obsolete file list.

## Control Flow
Locating lists or accepts a listing, scans marker filenames, opens the directory, and returns a handle plus current value. `Move` increments the iteration, creates a new marker file, syncs it, closes it, removes the old marker if present, and syncs the directory. `RemoveObsolete` deletes older marker files discovered during locate or failed old-file removal.

## State And Persistence
State is persisted entirely in marker filenames plus directory entries. Durability depends on syncing the new marker file before directory sync. A marker handle also keeps in-memory iteration and obsolete-file state. `SyncDir` exposes directory fsync for callers that need to make related files durable before marker movement.

## Dependencies And Integration Points
It depends on `vfs.FS`, `vfs.File`, Cockroach errors, and not-exist classification. `version_set.go` relies on this code for MANIFEST switching and uses `SyncDir` before `Move` to ensure the manifest exists durably before the marker points at it.

## Risks And Edge Cases
Marker names and values are encoded into filenames, so malformed `marker.` files cause scan errors. The abstraction is not safe for concurrent use across processes. If create returns an error after actually creating a file, a later locate treats it as obsolete. Directory sync errors panic because fsync errors are considered unrecoverable. Iteration can advance even when `filename` remains on the old value after a failed move.

## Test Signals
Tests should cover filename round trips, parse failures, selecting highest iteration, multiple marker names, empty markers, moves, obsolete cleanup, strict crashable-memory sync behavior, and injected filesystem errors with retry.
