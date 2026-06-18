# sources/sync-backup/kopia/repo/blob/throttling/token_bucket.go

Purpose: implements the rate-limiting primitive used by the throttler for operation and byte quotas.

Important APIs/types/functions: `tokenBucket` tracks name, time/sleep hooks, mutex, last refill time, current tokens, max tokens, and refill time unit. Methods are `replenishTokens`, `sleepDurationBeforeTokenAreAvailable`, `Take`, `TakeDuration`, `Return`, `SetLimit`, `sleepWithContext`, and `newTokenBucket`.

Control flow: `TakeDuration` replenishes tokens based on elapsed time, subtracts requested tokens, and returns zero if enough tokens remain or a duration proportional to the deficit. `Take` sleeps for that duration. `Return` refunds tokens up to max. `SetLimit` validates nonnegative limits and caps existing token count.

State and persistence behavior: token counts are in-memory and protected by a mutex. Limit zero means unlimited/no sleeping because `sleepDurationBeforeTokenAreAvailable` returns zero when `maxTokens == 0`.

Dependencies/integration: used by `tokenBucketBasedThrottler`; logging reports sleeps; tests override `now` and `sleep` hooks for deterministic time.

Risks and edge cases: the implementation intentionally allows `numTokens` to go negative to represent debt. `SetLimit` contains a duplicate assignment but is harmless. Context cancellation only affects the sleep helper, not token accounting already performed.

Test signals: `token_bucket_test.go` validates deterministic refill, sleeping, debt, max cap, and refund behavior.
