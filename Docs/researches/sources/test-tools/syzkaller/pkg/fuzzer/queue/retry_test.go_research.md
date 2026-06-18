# sources/test-tools/syzkaller/pkg/fuzzer/queue/retry_test.go

## Purpose
This file unit-tests the retry wrapper's status policy.

## Important APIs, Types, And Functions
`TestRetryerOnRestart` submits important and unimportant requests and repeatedly completes them as `Restarted`. `TestRetryerOnCrash` covers unimportant crash, important crash followed by success, and important crash followed by a second crash.

## Control Flow
Tests pull requests through `Retry(q)`, call `Done` with selected statuses, then check whether `Next` returns the same request again or nil. They also call `Wait` to ensure final delivered statuses match expectations.

## State And Persistence Behavior
The tests exercise retry queue state and the request's `onceCrashed` state.

## Dependencies And Integration Points
The file depends on `context`, `testing`, and `testify/assert`. It validates behavior relied on by fuzzer crash handling and `Request.Risky`.

## Risks
The restart loop test uses a fixed 10 iterations to represent unbounded retry. It does not cover `ExecFailure`, `Hanged`, callback stacking beyond retry, or context cancellation.

## Test Signals
Restarted requests must be returned repeatedly until success. Unimportant crashes complete immediately; important crashes get one retry only.
