# sources/sync-backup/git-lfs/tq/transfer_queue.go

Purpose: orchestration engine for batched Git LFS uploads/downloads, including API calls, adapter selection, duplicate-OID coalescing, progress, retries, delayed retries, watcher notifications, and error collection.

Important APIs/types/functions: `retryCounter`, `batch`, `abortableWaitGroup`, `TransferQueue`, `objects`, `objectTuple`, options (`DryRun`, `WithProgress`, `RemoteRef`, `WithProgressCallback`, `WithBatchSize`, `WithBufferDepth`), `NewTransferQueue`, `Upgrade`, `Add`, `remember`, `collectBatches`, `enqueueAndCollectRetriesFor`, `addToAdapter`, `partitionTransfers`, `handleTransferResult`, `useAdapter`, `ensureAdapterBegun`, `Wait`, `Watch`, retry helpers, and `Errors`.

Control flow: construction starts error and batch collector goroutines. `Add` upgrades manifest, records unique OIDs, sends only first object per OID to the incoming channel, and immediately notifies watchers for duplicates already completed. Collector fills batches, sorts largest first, calls batch API or standalone adapter, validates upload object presence, selects adapter, sends transfers, gathers retryable failures, and merges retries ahead of newly collected items. `Wait` closes incoming, waits for unique OIDs, stops adapter, closes watchers/error channel, flushes meter, and prints content-type advice after HTTP 422 upload failures.

State and persistence: in-memory queues/channels, transfer map guarded by mutex, retry counts, wait groups, adapter lifecycle state, unsupported-content-type flag, errors slice, and meter counters. No durable persistence, but adapters perform file/network side effects.

Dependencies and integration points: central user of `Manifest`, `Batch`, adapters, `Meter`, Git refs, `lfshttp` endpoints, Git LFS errors, and tools callbacks.

Risks: watcher slice is not guarded separately, so callers should set watchers before active concurrent use. Error collector appends without locking but runs single goroutine and is joined before final reads. Serious non-retriable batch errors abort the wait group. Delayed retry timing depends on wall clock. `q.meter` is called without nil checks in some paths, so callers generally supply a meter.

Test signals: `transfer_queue_test.go` covers retry defaults/backoff, batch size, and adapter reuse/switch rules; full concurrent transfer behavior is mostly integration-tested elsewhere.
