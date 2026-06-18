# sources/sync-backup/kopia/repo/maintenance/index_compaction.go

Purpose: runs quick-maintenance index compaction when the number of small index blobs is above a threshold.

Important APIs/types/functions: `runTaskIndexCompactionQuick`, `content.CompactOptions`, and `TaskIndexCompaction`.

Control flow: wraps `ContentManager().CompactIndexes` in `reportRunAndMaybeCheckContentIndex`, passing `MinSmallBlobs: 8` and current safety `DropContentFromIndexExtraMargin`.

State/persistence behavior: compacts persisted content indexes and records task run information in the encrypted maintenance schedule.

Dependencies/integration: called from quick maintenance after rewrite/delete decisions; integrates content manager compaction with maintenance stats and optional verification.

Risks/test signals: too-low compaction thresholds could churn indexes; too-high thresholds leave many small indexes. Covered indirectly by maintenance quick-run tests.
