# sources/sync-backup/kopia/repo/maintenancestats/stats_generate_range_checkpoint.go

Purpose: records the epoch range covered by a generated range checkpoint.

Important APIs/types/functions: `GenerateRangeCheckpointStats`, `WriteValueTo`, `Summary`, and `Kind`.

Control flow: writes min and max epoch fields and summarizes the inclusive range.

State/persistence behavior: stored in maintenance schedule extras for epoch range compaction.

Dependencies/integration: produced by `epoch.Manager.MaybeGenerateRangeCheckpoint`.

Risks/test signals: kind/JSON fields are covered by builder tests. Incorrect range semantics would affect maintenance observability rather than data directly.
