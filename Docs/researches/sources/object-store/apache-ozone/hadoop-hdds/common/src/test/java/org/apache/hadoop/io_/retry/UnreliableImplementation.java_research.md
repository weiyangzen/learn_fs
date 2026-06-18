# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/io_/retry/UnreliableImplementation.java

## Purpose
Provides a test implementation of `UnreliableInterface` with methods that succeed or fail in controlled ways for retry tests.

## Important APIs, types, and functions
- Implements `alwaysSucceeds`, `alwaysFailsWithFatalException`, `failsOnceThenSucceeds`, `failsTenTimesThenSucceeds`, `failsWithSASLExceptionTenTimes`, `failsWithAccessControlExceptionEightTimes`, and `failsWithWrappedAccessControlException`.
- Throws `IOException`, `SaslException`, `AccessControlException`, local `UnreliableException`, and `FatalException` depending on method.
- Maintains counters for controlled failure counts.

## Control flow
Each method increments internal counters and either throws until a threshold is reached or returns success immediately. Security-related methods throw exceptions that retry policies should not retry indefinitely.

## State and persistence behavior
State is in-memory call counters. No persistence.

## Dependencies and integration points
Used directly by `TestRetryProxy` as the target object behind retry proxies.

## Risks and test signals
If fixture behavior changes, retry tests may stop validating intended policy branches. Its value is deterministic failure sequencing.
