# sources/storage-engines/tikv/tests/failpoints/cases/test_gc_worker.rs

Purpose: tests GC worker handling of orphan versions emitted by write-CF compaction filters.

Important APIs and functions: `test_error_in_compaction_filter` injects `write_compaction_filter_flush_write_batch` and inspects `GcTask::OrphanVersions`. `test_orphan_versions_from_compaction_filter` starts auto GC in a raft cluster with mock safe point and region providers, then runs `sync_gc`.

Control flow: writes several versions and a delete, triggers compaction-filter GC, forces write-batch flushing failure, and verifies orphan default-CF versions are cleaned by the GC worker path.

State and persistence: MVCC write CF can be filtered before default CF cleanup, creating orphan default values. Tests check encoded `data_key` entries disappear.

Dependencies and integration: uses `TestGcRunner`, `GcWorker`, grpc KV client, raftstore clusters, `keys::data_key`, and transaction helpers.

Risks and test signals: polling loop waits for async cleanup. Signals protect cleanup handoff between compaction filter and GC worker.
