# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/RetriableTask.java

## Purpose
Wraps a `Callable<V>` with Hadoop `RetryPolicy` handling for local tasks.

## Important APIs, Types, And Functions
`RetriableTask<V>` implements `Callable<V>`. Constructor inputs are a `RetryPolicy`, a task name for logging, and the delegate `Callable<V>`. The key method is `call()`.

## Control Flow
`call()` invokes the delegate. On exception it increments attempts and asks `retryPolicy.shouldRetry(e, attempts, 0, true)`. `RETRY` sleeps the caller thread for `delayMillis` using `ThreadUtil.sleepAtLeastIgnoreInterrupts`; any other action breaks, logs a permanent failure, and throws an `IOException` wrapping the last cause.

## State And Persistence
State is only constructor configuration and local attempt counters during a call. There is no persistence and no cross-call attempt history.

## Dependencies And Integration Points
Uses Hadoop retry policy semantics and Ozone/Hadoop retry-policy factories. Intended for utility tasks that need retry behavior outside dynamic RPC proxies.

## Risks
Interrupts during retry sleep are ignored by `sleepAtLeastIgnoreInterrupts`, so shutdown responsiveness depends on the policy and delegate. Non-IO delegate exceptions are always wrapped into `IOException` after permanent failure. The idempotent flag is hard-coded true.

## Test Signals
`TestRetriableTask` covers success, retry-until-success, and max-retry failure. Extra tests should cover interrupted callers and policies that return failover actions.
