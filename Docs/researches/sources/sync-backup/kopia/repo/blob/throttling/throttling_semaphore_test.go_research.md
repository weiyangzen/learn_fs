# sources/sync-backup/kopia/repo/blob/throttling/throttling_semaphore_test.go

Purpose: verifies concurrency cap behavior of the throttling semaphore.

Important APIs/types/functions: `TestThrottlingSemaphore` uses `newSemaphore`, `SetLimit`, `Acquire`, and `Release`.

Control flow: the test first confirms default unlimited acquire/release and negative-limit error. For limits 3, 5, and 7, it starts ten goroutines each repeatedly acquiring, incrementing a protected concurrency counter, sleeping briefly, decrementing, and releasing; then it asserts max observed concurrency never exceeds the configured limit.

State and persistence behavior: only in-memory counters and semaphore channel state are used.

Dependencies/integration: depends on goroutines, wait groups, mutexes, time sleeps, and testify assertions.

Risks and edge cases: sleep makes the test probabilistic, so it asserts only upper bound and positivity instead of exact max concurrency.

Test signals: failures indicate the semaphore permits too many concurrent holders or fails to block at all.
