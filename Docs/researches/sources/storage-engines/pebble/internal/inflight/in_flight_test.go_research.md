# sources/storage-engines/pebble/internal/inflight/in_flight_test.go

## Purpose
`in_flight_test.go` verifies tracker reporting semantics and polling lifecycle behavior.

## Important APIs, Types, And Functions
`TestTrackerBasic` checks direct `Report` calls around one started operation. `TestPollingTracker` uses `testing/synctest` and an atomic value to observe reports from `NewPollingTracker`.

## Control Flow
The basic test starts a handle, waits past a millisecond threshold, expects non-empty report output, then stops the handle and expects empty output. The polling test advances synthetic time, checks no report before any operation, starts an operation, waits past max age, observes a report, stops it, and verifies no further reports after `Close`.

## State And Persistence Behavior
All state is test-local. Synctest controls time and goroutine scheduling deterministically. No files are used.

## Dependencies And Integration Points
It depends on Go 1.25 `testing/synctest`, `sync/atomic`, `time`, and `testify/require`. It directly tests public `inflight` APIs.

## Risks And Edge Cases
The tests assert report non-emptiness rather than exact stack output, avoiding path and timing brittleness. They do not test duplicate stack grouping or multiple shards directly.

## Test Signals
Passing tests signal threshold filtering, stop removal, periodic reporting, and `Close` suppression of future timer callbacks.
