# sources/sync-backup/kopia/internal/faketime/faketime_test.go

Purpose: validates deterministic test-clock helpers, including frozen values, auto-advancing sequences, manual advancement, and concurrent use.

Important APIs/types/functions: `Frozen`, `AutoAdvance`, `NewTimeAdvance`, `NewAutoAdvance`, `TimeAdvance.Advance`, and returned `NowFunc` closures. The tests also use `clock.Now`, `sync.WaitGroup`, and randomized manual advances.

Control flow: `TestFrozen` checks repeated reads for fixed timestamps. `TestAutoAdvance` launches three goroutines, records 60 returned timestamps, and asserts uniqueness. `TestTimeAdvance` checks manual advancement from a fixed base. `TestTimeAdvanceConcurrent` mixes random calls to `Advance` with auto-advance reads and checks per-goroutine order plus global uniqueness.

State/persistence behavior: no persistent state. The tests stress shared atomic state in `TimeAdvance`, especially that concurrent auto increments do not duplicate timestamps.

Dependencies/integration: these tests protect consumers such as cache expiry tests from flakes caused by wall-clock timing. They also indirectly validate that `TimeAdvance.NowFunc` closures share one receiver.

Risks/test signals: the concurrency test uses `math/rand` without a fixed seed and validates broad invariants rather than exact sequences. It would not catch negative `Advance` misuse because only positive advances are generated.
