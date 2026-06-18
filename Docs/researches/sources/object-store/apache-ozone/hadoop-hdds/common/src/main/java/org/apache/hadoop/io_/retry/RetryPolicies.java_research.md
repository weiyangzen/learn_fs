# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/io_/retry/RetryPolicies.java

## Purpose
Factory and implementation collection for Hadoop `RetryPolicy` strategies used by local tasks and RPC proxies.

## Important APIs, Types, And Functions
Public policies/factories include `TRY_ONCE_THEN_FAIL`, `RETRY_FOREVER`, `retryForeverWithFixedSleep`, `retryUpToMaximumCountWithFixedSleep`, `exponentialBackoffRetry`, and `failoverOnNetworkException`. Nested implementations include `TryOnceThenFail`, `RetryForever`, `RetryLimited`, `RetryUpToMaximumCountWithFixedSleep`, `ExponentialBackoffRetry`, and `FailoverOnNetworkExceptionRetry`.

## Control Flow
Limited policies fail when retry count reaches max and otherwise return retry with fixed or exponential randomized delay. Network failover policy fails on max failovers/retries, SASL failures, invalid tokens, and access denial; failovers on connect/EOF/no-route/unknown-host/timeouts and idempotent socket IO; retries retriable exceptions; delegates all other exceptions to fallback.

## State And Persistence
Policy instances are immutable configuration holders except cached `toString()` in `RetryLimited`. No persistence.

## Dependencies And Integration Points
Depends on Hadoop `RetryPolicy`, IPC `RemoteException`/`RetriableException`, network exceptions, security exceptions, SASL, and Java time units. Used by `RetriableTask`, `Client.ConnectionId`, and `RetryInvocationHandler`.

## Risks
`calculateExponentialTime` can cap to zero when `maxDelayBase` is zero, making failover retries immediate. Retry/failover counters must be interpreted consistently by callers. Wrapped access-control detection walks causes and may classify broad failures as non-retriable.

## Test Signals
`TestRetryProxy` covers fixed, forever, exponential, failover, retriable, and access-control cases. Additional tests should cover zero cap, SASL cause chains, and retry-vs-failover counter boundaries.
