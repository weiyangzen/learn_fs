# sources/user-network-fs/rclone/backend/sftp/stringlock_test.go

Purpose: concurrency test for `stringLock`.

Important APIs/types/functions: `TestStringLock` creates three counters, one shared lock, and many goroutines that repeatedly lock by counter ID, read-modify-write, then unlock.

Control flow: `outer` and `inner` constants create 1000 increments per key. Each critical section sleeps briefly to amplify race windows. After `WaitGroup` completion, the test asserts all counters reached the expected total.

State and persistence behavior: only in-memory counters and lock map. The test relies on deterministic final counts to prove same-ID serialization while allowing different IDs to run concurrently.

Dependencies/integration: uses `sync`, `time`, `fmt`, and `testify/assert`.

Risks/test signals: good signal for keyed mutual exclusion under contention, but it does not test panic behavior for invalid unlock or fairness/starvation.
