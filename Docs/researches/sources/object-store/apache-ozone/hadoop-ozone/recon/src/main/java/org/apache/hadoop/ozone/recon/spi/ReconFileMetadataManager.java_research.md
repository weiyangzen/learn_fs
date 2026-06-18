## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/ReconFileMetadataManager.java

Purpose: `ReconFileMetadataManager` defines DB operations for file-size bucket counts used by Recon file metadata tasks and APIs.

Important APIs and types: staged-manager creation, `reinitialize`, `batchStoreFileSizeCount`, `batchDeleteFileSizeCount`, `getFileSizeCount`, `getFileCountTable`, `commitBatchOperation`, and `clearFileCountTable`. Key type is `FileSizeCountKey`; values are `Long`.

Control flow: tasks write or clear file count buckets during incremental processing or full reprocess. Callers use batch operations for atomic updates, then commit through the manager.

State and persistence: implementations persist a RocksDB table keyed by file-size bucket descriptors. Staged managers allow rebuilding counts outside the active DB.

Dependencies and integration points: used by Recon tasks that compute file-size distributions from OM metadata. Integrates with `ReconDBProvider` for active DB switching.

Risks and edge cases: bucket consistency depends on callers deleting old bucket entries and storing new ones in the same batch when files change. `clearFileCountTable` is destructive and should be restricted to reprocess flows.

Test signals: tests should cover batch store/delete, clear behavior, staged manager use, and reinitialize after DB provider swap.
