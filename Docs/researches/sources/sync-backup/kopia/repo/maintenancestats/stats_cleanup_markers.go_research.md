# sources/sync-backup/kopia/repo/maintenancestats/stats_cleanup_markers.go

Purpose: records epoch marker and deletion watermark cleanup counts.

Important APIs/types/functions: `CleanupMarkersStats`, `WriteValueTo`, `Summary`, and `Kind`.

Control flow: writes marker/watermark counts to content logs and returns a compact human summary.

State/persistence behavior: stored as maintenance schedule extra data for epoch cleanup tasks.

Dependencies/integration: produced by epoch manager cleanup and registered in stats builder.

Risks/test signals: kind and JSON tags must remain aligned with builder tests and historical schedule data.
