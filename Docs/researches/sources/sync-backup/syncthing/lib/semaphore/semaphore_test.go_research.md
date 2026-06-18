# sources/sync-backup/syncthing/lib/semaphore/semaphore_test.go

Purpose: validates edge cases in the adjustable semaphore implementation.

Important tests: `TestZeroByteSemaphore` asserts zero-capacity semaphores are no-ops for large takes/gives. `TestByteSemaphoreCapChangeUp` proves a blocked waiter unblocks when capacity grows. `TestByteSemaphoreCapChangeDown1` and `TestByteSemaphoreCapChangeDown2` cover shrinking capacity while bytes are checked out, including the case where available becomes zero. `TestByteSemaphoreGiveMore` confirms oversized takes/gives are clamped and capacity increases only add the diff to available.

State and persistence: tests inspect the package-private `available` field directly. No persistence.

Dependencies and integration: tests only use `testing`; they are white-box tests in package `semaphore`.

Risks and signals: coverage is strong for arithmetic invariants but does not cover context cancellation, goroutine behavior, or `MultiSemaphore` rollback/order semantics.
