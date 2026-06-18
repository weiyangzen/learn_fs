<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/workshare/workshare_pool.go -->
# sources/sync-backup/kopia/internal/workshare/workshare_pool.go

- Purpose: Implements a generic fixed worker pool for opportunistic shared work.
- Important APIs/types/functions: `ProcessFunc`, `workItem`, `Pool`, `ActiveWorkers`, `NewPool`, `Close`.
- Control flow: `NewPool` creates unbuffered work channel, closed channel, semaphore, and worker goroutines. Workers receive items, increment active count, process, decrement, release semaphore token, and signal the item wait group. `Close` closes the pool and waits workers out.
- State and persistence: In-memory goroutines, channels, atomics, and wait group only.
- Dependencies and integration points: Paired with `AsyncGroup` in `workshare_waitgroup.go`.
- Risks and edge cases: A semaphore token is expected before sending work; misuse can deadlock or panic through the higher-level API.
- Test signals: `workshare_test.go` covers tree summing, worker counts, invalid usage, and benchmark path.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/workshare/workshare_pool.go -->
