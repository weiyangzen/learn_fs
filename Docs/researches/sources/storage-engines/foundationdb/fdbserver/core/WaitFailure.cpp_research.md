# sources/storage-engines/foundationdb/fdbserver/core/WaitFailure.cpp

## sources/storage-engines/foundationdb/fdbserver/core/WaitFailure.cpp

Purpose: implements the wait-failure RPC pattern used by server interfaces to detect endpoint failure through long-poll reply promises and the failure monitor.

Important APIs: `waitFailureServer`, `waitFailureClient`, `waitFailureClientStrict`, and `waitFailureTracker`.

Control flow and state: `waitFailureServer` stores incoming `ReplyPromise<Void>` objects in a deque. It does not reply unless the queue exceeds `MAX_OUTSTANDING_WAIT_FAILURE_REQUESTS`, at which point it releases the oldest promise. Cancellation breaks outstanding promises. `waitFailureClient` repeatedly sends a reply promise using `getReplyUnlessFailedFor`; absence of a reply indicates endpoint failure and optionally traces details. Successful replies are rate-limited by `WAIT_FAILURE_DELAY_LIMIT`. `waitFailureClientStrict` repeatedly detects failure and then waits for the endpoint to remain failed for `failureReactionTime` unless the failure monitor observes recovery. `waitFailureTracker` keeps an `AsyncVar<bool>` synchronized with the failure monitor and active wait-failure probes.

Dependencies and integration: depends on `fdbrpc` request streams, `IFailureMonitor`, Flow deque/delay, server knobs, task priorities, and trace events. It underpins liveness detection for worker, backup, data distributor, and other interfaces that expose `waitFailure`.

Risks and tests: queue overflow deliberately replies to old requests, so knob sizing affects detection latency and memory. Unknown errors assert. Tests should exercise failure, recovery before strict timeout, cancellation, queue overflow, trace context, and different task priorities.
