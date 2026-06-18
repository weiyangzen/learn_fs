# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/io_/retry/RetryInvocationHandler.java

## Purpose
Dynamic-proxy invocation handler that applies Hadoop retry and failover policy to method calls, including RPC call ID/retry-count propagation.

## Important APIs, Types, And Functions
`RetryInvocationHandler<T>` implements `RpcInvocationHandler`. Important nested types are `Call`, `Counters`, `ProxyDescriptor`, and `RetryInfo`. Key methods are `invoke`, `handleException`, `invokeMethod`, `isRpcInvocation`, `close`, and `getConnectionId`.

## Control Flow
`invoke()` detects whether the target is an RPC proxy, assigns a call ID, and loops while `Call.invokeOnce()` returns `RETRY`. A call invokes the method, catches exceptions, computes `RetryInfo` from the policy and idempotence annotations, sleeps until retry time, optionally performs failover once per expected failover count, increments retry/failover counters, and retries. Fail decisions rethrow the selected exception.

## State And Persistence
State includes current proxy provider/proxy, failover count, successful-call flag, a set of proxies failed at least once for log suppression, default and per-method policies, and per-call counters. No persistence.

## Dependencies And Integration Points
Integrates Hadoop retry annotations, `FailoverProxyProvider`, `MultiException`, Ozone-shaded IPC classes, `Client.setCallIdAndRetryCount`, `ProtocolTranslator`, and `RPC.getConnectionIdForProxy`.

## Risks
`failedAtLeastOnce` is a plain `HashSet` touched without synchronization. Method policy lookup by name ignores overload signatures. `SET_CALL_ID_FOR_TEST` is a global thread-local test hook. Reflection uses deprecated `isAccessible`.

## Test Signals
`TestRetryProxy` covers retry policies, failover behavior, `isRpcInvocation`, and failure limits. OM HA follower-read tests exercise call-ID test behavior and integration failover.
