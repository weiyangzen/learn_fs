## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/ReconGlobalStatsManager.java

Purpose: this SPI defines persistence for global Recon statistics, keyed by string and valued by `GlobalStatsValue`.

Important APIs and types: `getStagedReconGlobalStatsManager`, `reinitialize`, `batchStoreGlobalStats`, `getGlobalStatsValue`, `getGlobalStatsTable`, and `commitBatchOperation`.

Control flow: Recon tasks store derived global stats in batches, consumers read by key or table, and reprocess flows can use staged managers before active DB replacement.

State and persistence: implementations write to a RocksDB table of global stats. Batch operations support atomic multi-stat updates.

Dependencies and integration points: used by OM-derived tasks and dashboards for aggregate counts and sizes. Relies on `ReconDBProvider` for active/staged DB management.

Risks and edge cases: string keys are a loose contract; collisions or renames can break consumers. No delete or clear method is exposed in this interface, so stale stats require implementation-specific handling or overwrites.

Test signals: tests should cover staged reinitialization, batch commits, missing-key reads, and key naming compatibility.
