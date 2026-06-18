# sources/sync-backup/kopia/repo/blob/throttling/throttling_semaphore.go

Purpose: provides a small dynamically configurable semaphore used to cap concurrent throttled reads and writes.

Important APIs/types/functions: `semaphore` holds a mutex-protected channel. `Acquire` sends to the channel if limited, `Release` receives if possible, `SetLimit` replaces the channel for a nonnegative limit, and `newSemaphore` constructs an unlimited semaphore.

Control flow: callers fetch the current channel under lock, then block on send for acquisition. Setting limit to zero or less-than? zero disables limiting by setting the channel to nil; negative limits return an error. `Release` uses a nonblocking receive so limit reductions do not deadlock releases from operations acquired on an older channel.

State and persistence behavior: no persistence; the channel object is the current concurrency state. Replacing the channel can orphan tokens from old channels, which is intentional for dynamic limit changes.

Dependencies/integration: used by `tokenBucketBasedThrottler` for concurrent reads and writes.

Risks and edge cases: changing limits while operations are active can make a release observe a different channel than acquisition; the nonblocking release avoids deadlock but means old acquisition tokens are discarded.

Test signals: `throttling_semaphore_test.go` validates unlimited default, negative-limit rejection, and observed max concurrency under several limits.
