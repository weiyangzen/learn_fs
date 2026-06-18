# sources/sync-backup/kopia/repo/blob/throttling/throttler_test.go

Purpose: timing-based tests for token-bucket throttling limits across operation rates and bandwidth limits.

Important APIs/types/functions: `TestThrottler`, `TestThrottlerLargeWindow`, and helper `testRateLimiting` exercise `NewThrottler`, `BeforeDownload`, `ReturnUnusedDownloadBytes`, `BeforeUpload`, and `BeforeOperation`.

Control flow: `TestThrottler` creates limits and, for each limit type, starts three workers for three seconds that repeatedly perform throttled operations while accumulating totals. It asserts actual rate stays within 85% to 115% of target. The large-window test starts full, consumes a minute worth of download quota immediately, then verifies the next quota chunk blocks around one second.

State and persistence behavior: throttler state is in-memory token buckets and semaphores; tests use wall-clock timing through `clock.Now`/`timetrack`.

Dependencies/integration: depends on random sizes, goroutines, atomics, and testify. Timing margins account for scheduling variability.

Risks and edge cases: tests are inherently timing-sensitive and can be noisy on overloaded machines. They do not test dynamic `SetLimits` or update handlers.

Test signals: failures indicate token refill math, burst capacity, refund handling, or operation bucket mapping has regressed.
