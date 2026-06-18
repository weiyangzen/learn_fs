# sources/test-tools/syzkaller/pkg/manager/repro_test.go

Purpose: Tests the generic `ReproLoop` scheduler behavior with a mock `ReproManagerView`.

Important tests and helpers: `TestReproManager` checks initial capacity, VM reservation scaling, running set, and shutdown to zero reservations. `TestReproOrder` verifies manual dashboard crashes are prioritized over ordinary dashboard, which are prioritized over hub crashes, and that repeat entries can be processed after prior runs finish. `TestReproRWRace` validates same-title serialization and `NeedRepro` rechecking after a repro appears. `TestCancelRunningRepro` verifies loop exit while a repro is running. `TestEnqueueTriggersRepro` checks that the loop skips queued crashes that no longer need repro and reaches a later needed crash. `reproMgrMock` records reserved VMs and exposes run callbacks.

Control flow and state: Tests enqueue crashes, run `Loop` in goroutines, receive `runCallback` objects from the mock, then unblock them by sending `ReproResult`. `onVMShutdown` polls reservation count until the loop returns reserved VMs.

Dependencies and integration: Uses `report.Report`, context cancellation, atomics, and testify assertions. It validates scheduler-to-manager callback contracts without real repro execution.

Risks: Some tests rely on goroutine scheduling and polling. They do not validate `calculateReproVMs` over many pool sizes or HTTP reporting of repro state.

Test signals: Strong coverage for concurrency-sensitive scheduler decisions, especially same-title races and dynamic queue rechecking.
