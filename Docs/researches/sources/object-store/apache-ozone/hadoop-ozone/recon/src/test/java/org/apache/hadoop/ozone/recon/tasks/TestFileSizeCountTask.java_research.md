# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestFileSizeCountTask.java

Purpose: This suite verifies file-size histogram maintenance for `FileSizeCountTaskOBS` and `FileSizeCountTaskFSO`. It covers full reprocess from OM key/file tables and delta processing of PUT, UPDATE, and DELETE events into Recon's RocksDB-backed file metadata store.

Important APIs and types: The tests use `ReconFileMetadataManager`, `FileSizeCountTaskOBS`, `FileSizeCountTaskFSO`, `FileSizeCountKey`, `ReconConstants.FILE_SIZE_COUNT_TABLE_TRUNCATED`, `OMDBUpdateEvent`, `OMUpdateEventBatch`, `OmKeyInfo`, `OMMetadataManager`, `TypedTable`, `TableIterator`, and bucket layouts `OBJECT_STORE` and `FILE_SYSTEM_OPTIMIZED`.

Control flow: `setupOnce` creates a real Recon injector with SQL DB, Recon OM, and container DB and obtains `ReconFileMetadataManager`. `setUp` resets the table-truncation flag, creates OBS/FSO task instances, and deletes all rows from the file-count table. Reprocess tests mock table iterators returning controlled `OmKeyInfo` sequences. Process tests construct event batches and run both tasks over the same batch, then inspect persisted size buckets.

State and persistence behavior: The suite persists counts in the Recon file-count RocksDB table keyed by volume, bucket, and size-bin upper bound. Reprocess truncates and rebuilds counts; process increments on PUT, decrements old bins on DELETE or UPDATE, and increments new bins on UPDATE. Scale tests generate tens of thousands of synthetic keys across volumes and buckets to validate distribution and independence.

Dependencies and integration points: It validates Recon's file-size summary data used by namespace/utilization APIs and tests both OBS key-table and FSO file-table variants. It depends on file-size bin calculation, table names from OMDB definitions, and the shared truncation guard used by parallel task execution.

Risks: Some comments and expected bins are inconsistent with the concrete values, so the assertions are the authoritative signal. Running both OBS and FSO tasks on the same synthetic events can hide layout-filtering problems because each task may ignore different tables. Scale tests use many Mockito mocks, which can be slower and memory-heavy.

Test signals: Non-null `FileSizeCountKey` rows, exact counts for bins `1024`, `2048`, `16384`, `65536`, `131072`, and `Long.MAX_VALUE`, zero-or-null handling after deletion, unchanged counts for unaffected volumes, and successful task results from both reprocess variants.
