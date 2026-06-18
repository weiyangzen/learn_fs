# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ha/RetriableWithNoFailoverException.java

## Purpose
IOException marker indicating a request is retriable, but only against the same SCM server and without failover.

## Important APIs, Types, And Functions
Single constructor wraps an `IOException`.

## Control Flow
Retry policy should repeat the call on the current endpoint rather than rotating to another SCM.

## State And Persistence
Transient exception state only.

## Dependencies And Integration Points
Integrated by SCM HA client retry policy.

## Risks And Test Signals
No explicit delay/backoff is encoded; policy must supply it. Tests should distinguish no-failover retries from failover and non-retriable errors.
