# sources/sync-backup/kopia/repo/maintenancestats/stats_cleanup_superseded_indexes.go

Purpose: records cleanup of superseded epoch index blobs.

Important APIs/types/functions: `CleanupSupersededIndexesStats`, `WriteValueTo`, `Summary`, and `Kind`.

Control flow: stores max replacement time plus deleted blob count/size, writes them to content logs, and formats a summary.

State/persistence behavior: persisted in maintenance schedule extras for epoch index cleanup.

Dependencies/integration: produced by `epoch.Manager.CleanupSupersededIndexes` through maintenance run reporting.

Risks/test signals: time serialization and kind names are compatibility points covered by builder tests.
