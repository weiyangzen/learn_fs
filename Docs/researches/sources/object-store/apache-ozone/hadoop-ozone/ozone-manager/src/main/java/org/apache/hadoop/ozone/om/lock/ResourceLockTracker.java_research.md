# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/ResourceLockTracker.java

## Purpose
`ResourceLockTracker` is the abstract base for per-thread lock-order tracking and `OMLockDetails` collection. Concrete trackers implement resource-specific ordering rules.

## Important APIs and Types
It declares abstract `canLockResource(T)` and `getCurrentLockedResources()`. It provides `clearLockDetails`, `lockResource`, `unlockResource`, and `getOmLockDetails`. The backing `OMLockDetails` is a `ThreadLocal`.

## Control Flow
Before a lock operation, `OzoneManagerLock` or the hierarchical lock manager calls `clearLockDetails`. When a lock is successfully acquired, `lockResource` marks the thread-local details as acquired. `unlockResource` currently just returns the current details, leaving concrete subclasses to handle actual resource set updates if they override behavior.

## State and Persistence Behavior
State is per-thread and in-memory. There is no persistence. The returned `OMLockDetails` can be attached to OM responses so Ratis-applied writes still expose lock wait/held timings.

## Dependencies and Integration Points
The type parameter must implement `IOzoneManagerLock.Resource`. Concrete classes such as `LeveledResourceLockTracker` and `DAGResourceLockTracker` supply resource-order enforcement. `OzoneManagerLock.updateProcessingDetails` writes timing into this tracker when there is no Hadoop IPC call object.

## Risks and Edge Cases
The base class itself does not update a held-resource set; correctness depends on concrete subclasses. Since `OMLockDetails` is thread-local, work that crosses threads must explicitly merge or transfer details.

## Test Signals
Tests should verify concrete trackers clear and report details correctly, and that lock-acquired flags and timing values are visible through `getOmLockDetails`.
