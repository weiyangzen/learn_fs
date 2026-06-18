# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/container/common/helpers/TestExcludeList.java

## Purpose
Tests time-based cleanup semantics for `ExcludeList`, which tracks datanodes excluded from placement or replication decisions.

## Important APIs, types, and functions
- Uses `ExcludeList`, `DatanodeDetails`, `TestClock`, `Instant`, and `ZoneOffset`.
- Test cases are `excludeNodesShouldBeCleanedBasedOnGivenTime` and `excludeNodeShouldNotBeCleanedIfExpiryTimeIsZero`.

## Control flow
Tests add generated datanodes to the exclude list, advance a test clock, call cleanup, and assert membership changes according to expiry duration. A zero-expiry scenario verifies entries are retained.

## State and persistence behavior
The exclude list is in-memory operational state keyed by datanode identity. No persistence is involved.

## Dependencies and integration points
Placement, replication, and pipeline selection logic can consult `ExcludeList` to avoid failed or unsuitable datanodes.

## Risks and test signals
Over-aggressive cleanup can reintroduce bad nodes too soon; missing cleanup can starve placement. These tests signal expiry behavior around time boundaries.
