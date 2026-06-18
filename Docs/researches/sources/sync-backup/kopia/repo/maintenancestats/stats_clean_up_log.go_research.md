# sources/sync-backup/kopia/repo/maintenancestats/stats_clean_up_log.go

Purpose: captures log cleanup counts and byte totals.

Important APIs/types/functions: `CleanupLogsStats`, `WriteValueTo`, `Summary`, and `Kind`.

Control flow: writes to-delete, deleted, and retained counters into content logs; summary formats counts with human-readable byte strings.

State/persistence behavior: stats are persisted in maintenance schedule run extras after log cleanup.

Dependencies/integration: produced by `CleanupLogs` and reconstructed by `BuildFromExtra`.

Risks/test signals: field names are compatibility-sensitive for stored extras. Builder tests assert exact JSON.
