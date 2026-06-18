# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/io_/retry/TestRetryProxy.java

## Purpose
Tests Hadoop-compatible retry proxy behavior in the shaded `org.apache.hadoop.io_` retry package.

## Important APIs, types, and functions
- Uses `RetryProxy`, `RetryPolicies`, `RetryPolicy`, `RetryAction`, `RetryDecision`, `FailoverProxyProvider`, and the local `UnreliableInterface`/`UnreliableImplementation` fixtures.
- Covers try-once failure, RPC invocation metadata, retry forever, fixed sleep retry, maximum-count retry, exponential retry, interruptible retry, SASL no-retry, access-control no-retry, and wrapped access-control handling.
- Uses Mockito to delegate mocked policy decisions to real policies while capturing the final retry action.

## Control flow
Setup creates an unreliable implementation. Tests wrap it in `RetryProxy` with different policies, invoke methods that succeed, fail once, fail many times, or throw fatal/security exceptions, and assert call counts, returned results, thrown exceptions, and policy decisions.

## State and persistence behavior
State is in-memory retry counters inside `UnreliableImplementation` and captured retry actions. No persistence.

## Dependencies and integration points
This package preserves Hadoop retry semantics for Ozone code paths that use retry proxies without depending directly on Hadoop package names.

## Risks and test signals
Incorrect proxy logic can retry non-retriable security failures, fail to retry transient failures, or lose invocation metadata. The suite gives broad behavior signals for retry policy integration.
