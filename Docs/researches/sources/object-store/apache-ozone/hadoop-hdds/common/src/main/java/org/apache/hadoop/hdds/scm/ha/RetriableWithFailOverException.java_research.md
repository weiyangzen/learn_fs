# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ha/RetriableWithFailOverException.java

## Purpose
IOException marker indicating a request can be retried on another SCM server, triggering failover.

## Important APIs, Types, And Functions
Single constructor wraps an `IOException` cause.

## Control Flow
Client retry/failover policy catches this type and moves to the next SCM endpoint.

## State And Persistence
Transient exception state only.

## Dependencies And Integration Points
Integrated by SCM HA client proxies and retry policies.

## Risks And Test Signals
No message-only constructor may limit remote unwrap behavior compared with `NonRetriableException`. Tests should cover failover retry classification and cause preservation.
