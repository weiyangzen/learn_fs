# sources/sync-backup/kopia/repo/maintenancestats/stats_advance_epoch.go

Purpose: records whether epoch advancement ran and what the current epoch is.

Important APIs/types/functions: `AdvanceEpochStats`, `WriteValueTo`, `Summary`, and `Kind`.

Control flow: writes `currentEpoch` and `wasAdvanced` into content logs, summarizes either advancement or staying at the same epoch, and returns kind `advanceEpochStats`.

State/persistence behavior: instances are serialized into maintenance schedule extras and emitted to content logs.

Dependencies/integration: produced by epoch maintenance tasks in `maintenance_run.go` and handled by `BuildFromExtra`.

Risks/test signals: kind string must match builder switch. Builder tests cover JSON and reconstruction.
