# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/WaitFailure.h

## Purpose
This header declares reusable actors for server-role failure detection through `waitFailure` request streams.

## Important APIs, Types, And Functions
`waitFailureServer` serves a stream of `ReplyPromise<Void>` waiters. `waitFailureClient`, `waitFailureClientStrict`, and `waitFailureTracker` watch a remote waitFailure stream with configurable reaction time, slope, tracing, trace message, and task priority.

## Control Flow
Server roles expose a waitFailure endpoint and keep requests pending until they fail or stop. Clients issue requests and use delay/reaction settings to convert endpoint failure into actor completion or an `AsyncVar<bool>` update.

## State And Persistence Behavior
There is no persistent state. Failure observations are transient and affect role liveness decisions.

## Dependencies And Integration Points
It depends on `fdbrpc` and Flow futures. It integrates with master, TLog, resolver, ratekeeper, worker, and other role interfaces that include a `waitFailure` stream.

## Risks And Edge Cases
Too-short reaction windows cause false positives; too-long windows delay recovery. Strict and non-strict clients differ in tolerance and must match role semantics.

## Test Signals
Tests should verify failure detection after endpoint shutdown, reaction delays/slopes, tracker async updates, trace emission, and task-priority behavior under load.
