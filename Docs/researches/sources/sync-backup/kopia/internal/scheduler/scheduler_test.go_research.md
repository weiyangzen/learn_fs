# sources/sync-backup/kopia/internal/scheduler/scheduler_test.go

Purpose: validates scheduler triggering and refresh semantics.

Important APIs/types/functions: `TestScheduler`, `TestSchedulerWillTriggerItemsInThePast`, `TestSchedulerRefresh`, `TestTriggerNames`, and helper `reportTriggered`.

Control flow: supplies fake item lists and channels, starts schedulers with controlled times/refreshes, and asserts due callbacks fire in expected order and names are joined correctly.

State and persistence behavior: goroutine-local scheduler state; tests communicate through channels.

Dependencies and integration points: protects server scheduling behavior indirectly.

Risks and test signals: timing tests can be flaky if real sleeps are long; controlled time functions reduce this risk.
