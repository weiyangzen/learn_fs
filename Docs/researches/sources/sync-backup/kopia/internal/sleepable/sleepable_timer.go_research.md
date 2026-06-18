<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/sleepable/sleepable_timer.go -->
# sources/sync-backup/kopia/internal/sleepable/sleepable_timer.go

- Purpose: Implements a timer that fires at or soon after a target time while tolerating machine sleep by waking periodically.
- Important APIs/types/functions: `MaxSleepTime`, `Timer`, `Stop`, `NewTimer`.
- Control flow: `NewTimer` starts a goroutine that repeatedly calls `nowFunc`, closes the public channel once time is after the target, otherwise sleeps for `min(until-now, MaxSleepTime)`. `Stop` closes `stopChan` once and exits without closing `C`.
- State and persistence: State is a goroutine, `time.Timer`, stop channel, and `sync.Once`; there is no persistence.
- Dependencies and integration points: Uses only `sync` and `time`; callers can inject `nowFunc` for tests.
- Risks and edge cases: Exact equality with target time relies on timer granularity and `After` semantics; tests expect immediate behavior for now/past times.
- Test signals: `sleepable_timer_test.go` covers timing, stop behavior, concurrent stops, past/now targets, long waits, and channel closure semantics.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/sleepable/sleepable_timer.go -->
