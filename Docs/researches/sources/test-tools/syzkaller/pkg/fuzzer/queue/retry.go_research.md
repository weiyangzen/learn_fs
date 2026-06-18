# sources/test-tools/syzkaller/pkg/fuzzer/queue/retry.go

## Purpose
`Retry` is a source wrapper that requeues requests when executor/VM outcomes indicate retry is appropriate. It handles VM restarts and important-request crash retries before allowing completion to propagate.

## Important APIs, Types, And Functions
`retryer` holds a retry `PlainQueue` and a base `Source`. `Retry(base Source)` constructs the wrapper. `Next` prefers retry-queue entries using `tryNext`, otherwise pulls from base, and installs `done` as a completion callback. `done` decides whether to propagate completion or requeue.

## Control Flow
On `Success`, `ExecFailure`, or `Hanged`, `done` returns true and completion continues. On `Restarted`, the same request is requeued and completion is intercepted. On `Crashed`, an important request that has not crashed before is marked `onceCrashed`, requeued, and intercepted; otherwise the crash is delivered. Unknown statuses panic.

## State And Persistence Behavior
State is in memory. Retried requests are the same request objects, preserving waiters and callbacks. `onceCrashed` on `Request` records the one allowed important crash retry and is later exposed as `Risky`.

## Dependencies And Integration Points
It depends on `PlainQueue`, `Source`, `Request`, and `Result` from the same package. Fuzzer result processing checks `req.Risky()` to adjust candidate retry behavior after a crash.

## Risks
Restarted requests retry forever; a permanently restarting VM/source path can cause unbounded cycling. Because the same request object is reused, callbacks must be written to tolerate multiple intercepted completions. Important crashed requests are retried only once.

## Test Signals
`retry_test.go` verifies indefinite restart retry, no crash retry for unimportant requests, one crash retry for important requests, and no second crash retry.
