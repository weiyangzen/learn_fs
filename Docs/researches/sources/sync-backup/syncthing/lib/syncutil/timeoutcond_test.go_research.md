# sources/sync-backup/syncthing/lib/syncutil/timeoutcond_test.go

Purpose: stress-tests `TimeoutCond` for basic wait, broadcast, timeout, and lock behavior.

Important tests: `TestTimeoutCond` starts a periodic broadcaster and multiple routines waiting with staggered durations, each using `runLocks` for many iterations. `runLocks` ensures failed waits do not return significantly before their timeout and logs late successes as likely scheduler delay. The file also defines `testClock`, a manual clock helper unused by this test.

State and persistence: in-memory mutex, goroutines, timers, and result counters.

Dependencies and integration: tests locking and channel behavior under scheduling pressure.

Risks and signals: the test comments acknowledge timing instability. It is useful for deadlock detection but intentionally weak on exact success/failure counts.
