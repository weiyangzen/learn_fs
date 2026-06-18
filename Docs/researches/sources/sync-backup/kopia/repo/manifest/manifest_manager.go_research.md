# sources/sync-backup/kopia/repo/manifest/manifest_manager.go

Purpose: provides the public JSON manifest manager used for snapshots, maintenance params, and other repository metadata records.

Important APIs/types/functions: `Manager`, `ID`, `ErrNotFound`, `ContentPrefix`, `TypeLabelKey`, `Put`, `GetMetadata`, `Get`, `Find`, `Flush`, `Delete`, `Compact`, `IDsToStrings`, `IDsFromStrings`, `ManagerOptions`, and `NewManager`.

Control flow: `Put` requires a non-empty `type` label, generates a random hex ID, JSON-marshals payload, and stores a pending entry. Reads check pending first, then committed. `Find` merges pending and committed label matches and sorts by mod time. `Flush` commits pending entries through the committed manager. `Delete` creates a pending tombstone for an existing entry. `NewManager` configures time source and auto-compaction threshold.

State/persistence behavior: pending entries are in memory until flush; committed entries are persisted as content batches. Deletes are tombstones that become effective after merge and compaction.

Dependencies/integration: depends on content manager, compression, logging, metrics registry placeholder, random ID generation, and committed manager.

Risks/test signals: failing to flush loses pending manifests; duplicate labels are allowed; delete races are resolved by mod time. Tests cover put/get/find/delete/flush, corrupted content, invalid puts, auto-compaction thresholds, read-only behavior, and benchmarks.
