<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/problemspans/by_level.go -->
# sources/storage-engines/pebble/internal/problemspans/by_level.go

Purpose: concurrency-safe wrapper around per-level `Set`s of expiring problem spans, allowing LSM-level-specific overlap checks and global excision.

Important APIs/types: `ByLevel`, `Init`, `InitForTesting`, `IsEmpty`, `Add`, `Overlaps`, `Excise`, `Len`, and `String`.

Control flow and state: `Init` creates one `Set` per level and initializes the atomic empty fast-path. `Add` locks, clears the empty marker, and adds to the selected level. `Overlaps` returns false immediately if the atomic empty marker is true; otherwise it locks and delegates. `IsEmpty` scans all levels under lock and sets the atomic fast-path when all are empty. `Excise` applies removal to every level.

Persistence and integration: all state is in-memory and expiration is driven by `crtime.Mono`. Integrates with `problemspans.Set` and `base.UserKeyBounds`; likely used in compaction/read paths that need to avoid problematic key spans. Risks include required initialization, level index bounds panics, stale false in the empty fast-path until a scan, and coarse global mutex contention. Datadriven tests cover add/overlap/excise/empty behavior with mocked time.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/problemspans/by_level.go -->
