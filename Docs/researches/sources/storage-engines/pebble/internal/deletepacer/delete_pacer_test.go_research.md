# sources/storage-engines/pebble/internal/deletepacer/delete_pacer_test.go

## Purpose
`delete_pacer_test.go` validates the asynchronous delete pacer’s externally visible pacing behavior. It focuses on datadriven simulations for basic pacing, backlog catch-up, and low-free-space acceleration, plus targeted regression tests for close-time unblocking and queue-overflow fall-behind behavior.

## Important APIs, Types, And Functions
`TestDataDriven` runs the `backlog`, `basic`, and `free-space` datadriven files under Go 1.25 `testing/synctest`. `testState` holds the open `DeletePacer`, atomically mutable baseline rate and disk free space, enqueue/delete logs, and a semaphore used to block delete execution. `executeTest` interprets commands: `del`, `sleep`, `block-deletes`, `unblock-deletes`, `baseline-rate`, and `free-space`. `plot` renders enqueue/delete timelines. `TestCloseWithPacing` and `TestFallingBehind` exercise shutdown and queue pressure.

## Control Flow
Each datadriven `run` command constructs `Options`, `diskFreeSpaceFn`, and `deleteFn`, opens a pacer, executes scripted operations, waits for synctest quiescence after each command, and returns side-by-side enqueue/delete diagrams. The close test enqueues many slow-paced files and requires `Close` to finish within 30 seconds. The falling-behind test fills the queue past `maxQueueSize` and waits for the pacer to disable pacing enough to drain below the threshold.

## State And Persistence Behavior
All state is in-memory test state. Atomic fields model mutable configuration observed by the pacer. The semaphore intentionally serializes or blocks delete callbacks. There is no durable state; testdata golden files are the persistent expectations.

## Dependencies And Integration Points
The test depends on `datadriven`, `diagram`, `crhumanize`, `synctest`, Pebble `base.FileTypeTable`, `testutils.Logger`, and the package-level `Open`, `Enqueue`, and `Close` APIs defined outside this file. It also uses `MB`, `GB`, `RecentRateWindow`, and `maxQueueSize` from the deletepacer package.

## Risks And Edge Cases
Because the tests use synthetic time, any goroutine leak or missing synctest wait can cause flaky diagrams. The plot compresses events into 100 columns and can hide small timing differences. The close test is intentionally wall-clock bounded and would become expensive if pacing were not disabled during close.

## Test Signals
Golden output confirms pacing cadence changes across baseline, backlog, and free-space scenarios. Targeted tests signal that close is prompt even with outstanding debt, and that an oversized queue drops back below `maxQueueSize`.
