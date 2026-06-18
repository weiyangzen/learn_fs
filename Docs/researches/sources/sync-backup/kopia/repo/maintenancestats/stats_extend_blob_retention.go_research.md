# sources/sync-backup/kopia/repo/maintenancestats/stats_extend_blob_retention.go

Purpose: records object-lock retention extension results.

Important APIs/types/functions: `ExtendBlobRetentionStats`, `WriteValueTo`, `Summary`, and `Kind`.

Control flow: writes to-extend count, extended count, and retention period string; summary reports the same.

State/persistence behavior: persisted as full-maintenance extra data when object-lock extension is enabled.

Dependencies/integration: produced by `extendBlobRetentionTime` and handled by the stats builder.

Risks/test signals: retention period is a string rather than duration type, so formatting is part of the contract. Tests assert exact JSON.
