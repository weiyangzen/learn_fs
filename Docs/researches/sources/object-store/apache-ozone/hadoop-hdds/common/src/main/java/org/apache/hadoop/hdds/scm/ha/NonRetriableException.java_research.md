# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ha/NonRetriableException.java

## Purpose
IOException marker indicating an SCM HA client request should not be retried.

## Important APIs, Types, And Functions
Constructors accept a message for remote unwrap or an `IOException` cause wrapper.

## Control Flow
HA client/proxy code can classify this exception and stop retry loops.

## State And Persistence
Only inherited exception state; no persistence.

## Dependencies And Integration Points
Depends on `IOException`. Integrated by SCM HA retry policies and Hadoop RPC unwrapping.

## Risks And Test Signals
Cause-wrapping constructor uses `super(exception)`, so message is derived from cause. Tests should cover retry policy classification and remote unwrap.
