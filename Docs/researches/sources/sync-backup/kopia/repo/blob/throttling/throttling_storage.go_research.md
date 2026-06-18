# sources/sync-backup/kopia/repo/blob/throttling/throttling_storage.go

Purpose: wraps `blob.Storage` so all storage calls pass through a `Throttler` for operation, byte, and concurrency control.

Important APIs/types/functions: `Throttler` defines before/after operation hooks plus upload/download byte acquisition and download refund. `throttlingStorage` embeds `blob.Storage` and overrides `GetBlob`, `GetMetadata`, `ListBlobs`, `PutBlob`, `DeleteBlob`, and `ExtendBlobRetention`. `NewWrapper` constructs the wrapper.

Control flow: each operation calls `BeforeOperation`, defers `AfterOperation`, and delegates to the base storage. `GetBlob` pre-acquires requested length or a 20 MB estimate for unknown full reads, resets output, delegates, then acquires more or refunds unused bytes based on actual output length. `PutBlob` acquires upload bytes equal to data length before delegating.

State and persistence behavior: no durable state; throttling state lives in the supplied throttler and data persists only through the wrapped storage.

Dependencies/integration: typically used with `tokenBucketBasedThrottler` and provider options embedding `throttling.Limits`. It preserves the rest of the base storage interface through embedding.

Risks and edge cases: a failed full read with no bytes refunds the full 20 MB estimate. `ExtendBlobRetention` uses its own operation name, but the concrete token-bucket throttler currently ignores that name, so it only gets before/after callback visibility.

Test signals: `throttling_storage_test.go` checks exact wrapper call ordering, unknown-length estimates/refunds, extra acquisition for large downloads, partial-read byte acquisition, upload byte acquisition, and operation hooks.
