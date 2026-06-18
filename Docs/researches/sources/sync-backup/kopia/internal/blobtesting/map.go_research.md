## sources/sync-backup/kopia/internal/blobtesting/map.go

Purpose: in-memory `blob.Storage` implementation for tests, with optional capacity limit and timestamp control.

Important APIs/types/functions: `DataMap`, `NewMapStorage`, `NewMapStorageWithLimit`, `mapStorage`, and methods `GetBlob`, `GetMetadata`, `PutBlob`, `DeleteBlob`, `ListBlobs`, `TouchBlob`, and `GetCapacity`.

Control flow, state, and persistence: data and timestamps live in maps protected by an RW mutex. `PutBlob` rejects retention and do-not-recreate options, enforces optional byte limit, updates total bytes accounting, and supports set/get mod time. Listing snapshots matching keys, sorts them, then fetches metadata per key.

Dependencies and integration points: primary fake storage for cache, blobtesting verification, and many repository tests.

Risks and test signals: `DeleteBlob` is a no-op for missing IDs, matching tolerant storage behavior. `data.WriteTo` errors are ignored. Tests cover storage contract and capacity accounting.
