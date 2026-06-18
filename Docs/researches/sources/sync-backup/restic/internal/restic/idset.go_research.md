
# sources/sync-backup/restic/internal/restic/idset.go

Purpose: implements `IDSet`, a map-backed set for repository object IDs.

Important APIs include `NewIDSet`, `Has`, `Insert`, `Delete`, `Len`, `List`, `String`, `Merge`, `Equals`, `Clone`, `Sub`, `Intersect`, and `HasSubset`. `List` returns sorted IDs to make output deterministic. `Clone` uses `maps.Clone` for safe snapshots.

State is in-memory but represents persistent repository objects such as packs, indexes, locks, and files selected for removal or repack. Integration points include prune plans, repair index, lock exclusion sets, pack listing, and parallel removal. Risks include mutating shared sets across goroutines, relying on map iteration order without `List`, and confusing set operations with list order. Tests cover core set operations, list/string behavior, subset/intersection/subtraction, and equality.
