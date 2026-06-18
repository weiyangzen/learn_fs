# sources/sync-backup/kopia/repo/maintenancestats/stats_compact_indexes.go

Purpose: records the cutoff used when compacting indexes and dropping deleted content entries.

Important APIs/types/functions: `CompactIndexesStats`, `WriteValueTo`, `Summary`, and `Kind`.

Control flow: emits `droppedContentsDeletedBefore` and summarizes the cutoff timestamp.

State/persistence behavior: stored as schedule extra data after index compaction/drop-deleted tasks.

Dependencies/integration: produced by `dropDeletedContents` and reconstructed by stats builder.

Risks/test signals: timestamp meaning must align with safety logic in maintenance. Builder tests assert JSON shape.
