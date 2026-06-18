# sources/sync-backup/kopia/repo/maintenancestats/stats_snapshot_gc.go

Purpose: records snapshot garbage collection results across unreferenced, deleted, recent, in-use, system, and recovered contents.

Important APIs/types/functions: `SnapshotGCStats`, `WriteValueTo`, `Summary`, and `Kind`.

Control flow: writes all content counters/sizes to a content log JSON object and generates a summary string covering deletion, retention, in-use, and recovery.

State/persistence behavior: persisted in maintenance schedule extras for snapshot GC runs.

Dependencies/integration: used by snapshot maintenance and stats builder.

Risks/test signals: summary currently formats raw byte numbers for some fields rather than `units.BytesString`, unlike other stats. Builder tests assert JSON structure and reconstruction.
