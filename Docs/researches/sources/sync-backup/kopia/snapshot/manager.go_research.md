# sources/sync-backup/kopia/snapshot/manager.go

Purpose: manages snapshot manifests in the repository: listing sources, listing/loading/saving/updating snapshots, finding snapshots by root object, and locating previous manifests for incremental snapshots.

Important APIs/types/functions: constants `ManifestType`, `UsernameLabel`, `HostnameLabel`, and `PathLabel`; `ErrSnapshotNotFound`; functions `ListSources`, `ListSnapshots`, `LoadSnapshot`, `SaveSnapshot`, `LoadSnapshots`, `ListSnapshotManifests`, `FindSnapshotsByRootObjectID`, `UpdateSnapshot`, and `FindPreviousManifests`.

Control flow: snapshot source labels are converted by `sourceInfoToLabels` and `sourceInfoFromLabels`. Listing uses repository manifest label searches. Loading validates manifest type and maps missing manifests to `ErrSnapshotNotFound`. Saving validates host/user/path, clears `man.ID`, merges tags into labels while rejecting duplicate reserved keys, writes the manifest, and updates `man.ID`. `LoadSnapshots` launches goroutines with a 50-item semaphore and filters failed loads. `FindPreviousManifests` selects the latest complete snapshot and incomplete snapshots after it, optionally bounded by time.

State and persistence behavior: snapshot manifests persist through repository manifests with source labels plus optional tags. `UpdateSnapshot` writes a new manifest and deletes the old ID if changed. `LoadSnapshots` ignores failed individual loads after logging, so partially corrupt/missing sets can return successful subsets.

Dependencies/integration: depends on repository manifest APIs, `fs.UTCTimestamp`, `object.ID`, logging, and snapshot manifest structures from `manifest.go`.

Risks: concurrent `LoadSnapshots` writes distinct slice indexes but silently drops failures, which callers must tolerate. Tag keys colliding with reserved labels are rejected to preserve query semantics. Source label identity is sensitive to host/user/path normalization.

Test signals: likely covered by snapshot manager tests elsewhere; policy expiration code depends on listing snapshots from this file.
