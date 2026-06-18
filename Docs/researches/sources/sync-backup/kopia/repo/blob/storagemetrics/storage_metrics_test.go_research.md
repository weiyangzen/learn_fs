# sources/sync-backup/kopia/repo/blob/storagemetrics/storage_metrics_test.go

Purpose: validates that the storage metrics wrapper records bytes, item counts, latency distribution samples, errors, and pass-through metadata correctly.

Important APIs/types/functions: test cases are operation-specific: `TestStorageMetrics_PutBlob`, `GetBlob`, `GetMetadata`, `GetCapacity`, `DeleteBlob`, `Close`, `FlushCaches`, `ListBlobs`, and `Misc`. `requireCounterValue` checks registry snapshots.

Control flow: tests wrap in-memory map storage with `blobtesting.NewFaultyStorage`, configure one injected fault for an operation, call the operation once expecting the injected error and again expecting normal behavior, then assert error counters and duration distribution counts. Get/list tests also verify byte and item counters.

State and persistence behavior: map storage holds small test blobs; metrics state is in `metrics.Registry` snapshots. Faulty storage mutates its fault list as operations consume configured faults.

Dependencies/integration: depends on blobtesting fault injection, gather buffers, metrics registry snapshots, and the storagemetrics wrapper.

Risks and edge cases: there is no test for `ExtendBlobRetention`, leaving a gap around the uninitialized retention metric fields in `NewWrapper`.

Test signals: success proves normal and failing operations are counted once, full/partial downloads are distinguished, uploads count only on success, and base connection info/display name are preserved.
