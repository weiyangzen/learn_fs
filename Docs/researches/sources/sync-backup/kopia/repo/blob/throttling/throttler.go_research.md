# sources/sync-backup/kopia/repo/blob/throttling/throttler.go

Purpose: implements a configurable token-bucket-based throttler for blob operation rates, byte bandwidth, and concurrent read/write limits.

Important APIs/types/functions: `SettableThrottler` extends `Throttler` with `Limits`, `SetLimits`, and `OnUpdate`; `Limits` contains per-second operation and byte limits plus concurrency caps. `tokenBucketBasedThrottler` owns operation buckets, byte buckets, semaphores, current limits, update handlers, and a rate window. `NewThrottler` constructs and validates it.

Control flow: `BeforeOperation` consumes list/read/write operation tokens and acquires read/write semaphores for metadata/get and put/delete. `AfterOperation` releases the matching semaphore. Upload/download methods consume or return byte tokens. `SetLimits` applies all limits to buckets/semaphores under lock, rolls back on validation failure, stores limits, and invokes update handlers.

State and persistence behavior: all state is in memory: token counts, semaphore channels, current limits, and callbacks. No durable persistence is involved.

Dependencies/integration: used by `throttling_storage.go` and embedded provider options. Depends on the local `tokenBucket` and `semaphore` types.

Risks and edge cases: update handlers run under the mutex, so callbacks must avoid reentering throttler methods. `BeforeOperation` does not rate-limit `ExtendBlobRetention` in the current switch even though the wrapper names the operation.

Test signals: `throttler_test.go` measures read/write/list/upload/download rates and large-window burst behavior under concurrent workers.
