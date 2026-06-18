# sources/sync-backup/kopia/repo/blob/throttling/token_bucket_test.go

Purpose: deterministic unit test for token bucket refill, debt, sleep duration, and refund behavior.

Important APIs/types/functions: `TestTokenBucket` constructs a bucket, overrides `now` and `sleep`, and uses helper `verifyTakeTimeElapsed`.

Control flow: the test consumes zero/all tokens, takes more than available to force 500 ms sleep and negative token debt, advances fake time, verifies refill to max, consumes sequential chunks, forces one-second and 100 ms waits, and checks `Return` caps tokens at max.

State and persistence behavior: fake current time advances only through the test sleep hook or explicit `advanceTime`; bucket state remains in memory.

Dependencies/integration: depends on context, time, and testify assertions.

Risks and edge cases: because the test accesses package-private fields, it catches internal accounting changes but may need updates for alternate implementations.

Test signals: failures indicate broken refill math, max-token capping, debt handling, or refund behavior.
