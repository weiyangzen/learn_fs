# sources/sync-backup/kopia/internal/faketime/faketime.go

Purpose: provides deterministic and controllable time sources for tests. It avoids direct dependence on wall-clock time by returning functions compatible with code that expects `func() time.Time`.

Important APIs/types/functions: `Frozen`, `AutoAdvance`, `TimeAdvance`, `NewTimeAdvance`, `NewAutoAdvance`, `TimeAdvance.NowFunc`, `TimeAdvance.Advance`, `ClockTimeWithOffset`, `NewClockTimeWithOffset`, and `ClockTimeWithOffset.Advance`. `TimeAdvance` stores nanosecond deltas in `atomic.Int64`; `ClockTimeWithOffset` protects a mutable offset with a mutex.

Control flow: `Frozen` returns a closure over a fixed timestamp. `AutoAdvance` creates a `TimeAdvance` whose `NowFunc` atomically adds `autoDt` and returns the previous position, yielding `start`, then `start+dt`, and so on. Manual `Advance` mutates the same delta so future reads observe the jump.

State/persistence behavior: all state is in memory and test-scoped. `TimeAdvance` is monotonic under concurrent calls if advances are positive; `ClockTimeWithOffset` follows real `clock.Now()` plus a mutable offset rather than a frozen base.

Dependencies/integration: imports `internal/clock` for real clock reads in offset mode. It is used by storage/cache tests that need deterministic expiry or timestamp generation.

Risks/test signals: `NowFunc` returns a new closure each call but all closures share the same receiver state. Negative manual advances are not prohibited, so callers that require monotonic test time must avoid them.
