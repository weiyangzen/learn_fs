# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/io_/retry/CallReturn.java

## Purpose
Internal value object representing one retry-proxy invocation outcome: returned value, thrown exception, or retry instruction.

## Important APIs, Types, And Functions
Package-private `CallReturn` has enum `State { RETURNED, EXCEPTION, RETRY }`, static singleton `RETRY`, constructors for return values and throwables, `getState()`, and `getReturnValue()`.

## Control Flow
`getReturnValue()` rethrows the stored throwable for `EXCEPTION`, returns the stored value for `RETURNED`, and rejects use when state is `RETRY`.

## State And Persistence
Immutable per-call result state only; no persistence.

## Dependencies And Integration Points
Used by `RetryInvocationHandler.Call.invokeOnce()` to separate retry loop control from method result/exception propagation.

## Risks
It stores `Throwable`, so `getReturnValue()` can throw non-`Exception` errors. `RETRY` carries no delay data; delay and failover state live in the surrounding call object.

## Test Signals
`TestRetryProxy` indirectly covers retry handling. Direct tests could assert returned null values, exception propagation, and invalid `RETRY.getReturnValue()`.
