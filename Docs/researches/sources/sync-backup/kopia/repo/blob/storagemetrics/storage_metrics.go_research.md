# sources/sync-backup/kopia/repo/blob/storagemetrics/storage_metrics.go

Purpose: wraps any `blob.Storage` with metrics counters and latency distributions for storage operations, bytes transferred, list item counts, and errors.

Important APIs/types/functions: `blobMetrics` holds the wrapped storage plus counters/distributions. It implements all `blob.Storage` methods, recording durations for `GetBlob`, `GetCapacity`, `GetMetadata`, `PutBlob`, `DeleteBlob`, `ExtendBlobRetention`, `ListBlobs`, `Close`, and `FlushCaches`. `NewWrapper` creates metric instruments in a `metrics.Registry`.

Control flow: each method starts a timer, delegates to the base storage, observes duration, increments an error counter when appropriate, and updates byte or item counters. `GetBlob` separates full reads (`length < 0`) from partial reads, counting actual output length. `ListBlobs` wraps the callback to count delivered items.

State and persistence behavior: no durable state; metrics live in the provided registry. The wrapper preserves connection info, display name, read-only state, and base errors.

Dependencies/integration: used by repository managers to expose blob I/O observability; depends on internal metrics and timetrack packages plus the blob interface.

Risks and edge cases: `ExtendBlobRetention` creates fields but `NewWrapper` currently does not initialize `extendBlobRetentionDuration` or `extendBlobRetentionErrors`, so calling it through this wrapper would panic. Tests do not cover that method.

Test signals: `storage_metrics_test.go` verifies counters and duration counts for put/get/metadata/capacity/delete/close/flush/list and pass-through metadata methods.
