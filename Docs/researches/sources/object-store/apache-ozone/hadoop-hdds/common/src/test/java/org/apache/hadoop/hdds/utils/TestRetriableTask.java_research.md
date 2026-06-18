# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/TestRetriableTask.java

## Purpose
Tests `RetriableTask` execution behavior under success, transient failures, and retry-policy termination.

## Important APIs, types, and functions
- Uses `RetriableTask`, Hadoop `RetryPolicy`, `RetryPolicies`, `TimeUnit`, `AtomicInteger`, `IOException`, and `ZipException`.
- Test cases are `returnsSuccessfulResult`, `returnsSuccessfulResultAfterFailures`, and `respectsRetryPolicy`.

## Control flow
The tests construct tasks that either return immediately, fail a fixed number of times before succeeding, or fail with a policy-controlled exception. They assert returned results and retry counts/policy outcomes.

## State and persistence behavior
State is limited to in-memory retry counters and exceptions. No persistence.

## Dependencies and integration points
`RetriableTask` wraps retry policy behavior used by HDDS operations that need transient failure tolerance.

## Risks and test signals
Incorrect retry-loop control can cause premature failure, infinite retries, or ignored exception classes. These tests signal basic policy adherence.
