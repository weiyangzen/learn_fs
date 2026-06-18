<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/sleepable/sleepable_timer_test.go -->
# sources/sync-backup/kopia/internal/sleepable/sleepable_timer_test.go

- Purpose: Tests sleepable timer timing, stopping, concurrency, and channel behavior.
- Important APIs/types/functions: `testMaxSleepTime`, `setMaxSleepTimeForTest`, `TestNewTimer`, `TestTimerStop`, `TestTimerConcurrentStop`, `TestTimerEdgeCases`, `TestTimerChannelBehavior`.
- Control flow: Tests lower `MaxSleepTime`, create timers against `clock.Now`, wait on channels, stop timers before/after firing, and assert timing tolerances.
- State and persistence: Uses package global `MaxSleepTime` with cleanup restoration and temporary goroutines.
- Dependencies and integration points: Uses `clock`, `sync`, `testing`, and `time`.
- Risks and edge cases: Real-time sleeps can be flaky under heavy load, though tolerances are broad and durations are short.
- Test signals: Direct coverage for `sleepable_timer.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/sleepable/sleepable_timer_test.go -->
