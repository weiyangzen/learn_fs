# sources/sync-backup/kopia/repo/maintenancestats/stats_compact_single_epoch.go

Purpose: records stats from compacting one epoch of index blobs.

Important APIs/types/functions: `CompactSingleEpochStats`, `WriteValueTo`, `Summary`, and `Kind`.

Control flow: writes superseded blob count, total size, and epoch number; summary formats size and epoch.

State/persistence behavior: persisted as maintenance run extra data for quick/full epoch maintenance.

Dependencies/integration: produced by `epoch.Manager.MaybeCompactSingleEpoch`.

Risks/test signals: builder tests cover exact JSON; maintenance quick tests assert this task records runs.
