# sources/object-store/minio/cmd/leak-detect_test.go

## Purpose

`leak-detect_test.go` provides test-only goroutine leak detection helpers. It snapshots relevant goroutine stacks before a test and compares them after the test, retrying briefly to allow legitimate goroutines to exit.

## Important APIs, Control Flow, And State

`LeakDetect` holds a map of relevant stack dumps. `NewLeakDetect` calls `pickRelevantGoroutines` and stores the initial set. `CompareCurrentSnapshot` returns stacks present now but absent in the initial snapshot. `DetectLeak` exits early if the test already failed, then retries until either no leaked stacks remain or a five-second deadline expires, sleeping 50 ms between checks. On timeout it reports each leaked stack through the `TestErrHandler` interface. `DetectTestLeak` is the public helper intended for `defer DetectTestLeak(t)()`.

`ignoredStackFns` filters known testing/runtime/signal/snapshot stacks. `isIgnoredStackFn` returns true when a stack contains one of the ignored markers. `pickRelevantGoroutines` uses `debug.Stack`, splits goroutine dumps on blank lines, trims the stack body, skips testing runners and ignored functions, sorts the remaining stacks, and returns them.

State is only the in-memory snapshot. Dependencies are `runtime/debug`, `sort`, `strings`, and `time`.

## Risks And Test Signals

Risks are false positives from long-lived background goroutines, false negatives from overly broad ignored substrings, and reliance on textual stack formatting. The helper itself has no direct tests in this file. Its value is visible in tests that opt into `DetectTestLeak`; this file should be treated as test infrastructure rather than production behavior.
