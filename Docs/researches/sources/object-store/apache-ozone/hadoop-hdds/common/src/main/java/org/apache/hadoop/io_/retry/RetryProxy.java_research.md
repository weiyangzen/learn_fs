# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/io_/retry/RetryProxy.java

## Purpose
Factory for dynamic proxies whose method calls are handled by `RetryInvocationHandler`.

## Important APIs, Types, And Functions
`create(Class<T>, T implementation, RetryPolicy)` wraps a concrete implementation in `DefaultFailoverProxyProvider`. `create(Class<T>, FailoverProxyProvider<T>, RetryPolicy)` builds a JDK dynamic proxy implementing the requested interface.

## Control Flow
Both factories end in `Proxy.newProxyInstance` using the provider interface class loader and a new retry handler.

## State And Persistence
No static mutable state. Each created proxy owns handler/provider state in memory.

## Dependencies And Integration Points
Depends on Java reflection proxy APIs and Hadoop retry/failover provider interfaces. Used by RPC clients and local retry wrappers.

## Risks
The returned type is `Object`, so callers must cast. The proxy implements only the supplied `iface`; extra implementation interfaces are not exposed. Class-loader mismatches can fail at proxy creation.

## Test Signals
`TestRetryProxy` validates creation, retries, failovers, and annotation-based idempotence behavior through this factory.
