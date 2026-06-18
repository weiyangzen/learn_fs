# sources/distributed-fs/tahoe-lafs/src/allmydata/history.py

## Purpose
Keeps lightweight in-memory status history for recent Tahoe operations, mainly for status displays and counters. It tracks downloads, uploads, mutable map updates/publishes/retrieves, and helper uploads.

## Important APIs, Types, And Functions
`History` exposes `add_download`, `add_upload`, `notify_mapupdate`, `notify_publish`, `notify_retrieve`, and `notify_helper_upload` to register operation status objects. `list_all_*` methods iterate weak-key dictionaries for all still-live status objects. `recent_*` lists retain bounded recent items using module constants such as `MAX_DOWNLOAD_STATUSES` and `MAX_RETRIEVE_STATUSES`.

## Control Flow
Each add/notify method inserts the status object into a `WeakKeyDictionary`, appends it to the matching recent list, and pops oldest entries until the list fits its limit. Publish/retrieve notifications additionally update `stats_provider` counters when present.

## State And Persistence
All state is process-local and non-persistent. Weak dictionaries avoid keeping old status objects alive solely through history, while recent lists intentionally hold strong references to a bounded number of recent operations. Stats are delegated to the injected provider.

## Dependencies And Integration Points
Depends only on `weakref`. Downloader filenodes add `DownloadStatus` through `History.add_download`; upload and mutable subsystems use the corresponding notify methods; web/status views can enumerate these collections.

## Risks And Edge Cases
`stats_provider` is optional but `DownloadNode.read()` assumes `history.stats_provider` is usable when history exists, so callers should pass a fully initialized history or `None`. Recent-list strong references can keep the last N status objects alive even after weak dictionaries would otherwise drop them. Iteration order over weak dictionaries is not a stable status ordering.

## Test Signals
Coverage is mostly indirect through status, upload/download, and system tests rather than a dedicated history test. Useful probes are downloader status tests and mutable publish/retrieve tests that assert counters and visible status lists.
