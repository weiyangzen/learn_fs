# sources/sync-backup/kopia/repo/maintenance/cleanup_logs.go

Purpose: deletes old repository log blobs according to count, age, and total-size retention limits.

Important APIs/types/functions: `LogRetentionOptions`, `OrDefault`, `defaultLogRetention`, and `CleanupLogs`.

Control flow: default limits are applied when all limits are unset. `CleanupLogs` lists `_`-prefixed log blobs, sorts newest first, walks until keeping another blob would violate size, count, or age limits, then deletes the suffix unless dry-run is set.

State/persistence behavior: deletes persisted log blobs from blob storage and returns retained/to-delete/deleted counts and sizes in `CleanupLogsStats`.

Dependencies/integration: uses blob listing/deletion, `clock.Now`, content logging, and `maintenancestats.ToUint64`.

Risks/test signals: sorting by timestamp is central; incorrect ordering could delete recent logs. Dry-run preserves blobs while reporting planned deletions. Covered indirectly by maintenance schedule/report tests and stats serialization tests.
