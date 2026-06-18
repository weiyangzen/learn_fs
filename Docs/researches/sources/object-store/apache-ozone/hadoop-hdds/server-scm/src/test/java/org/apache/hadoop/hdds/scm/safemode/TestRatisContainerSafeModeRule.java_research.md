# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestRatisContainerSafeModeRule.java

## Purpose
`TestRatisContainerSafeModeRule` applies the shared container safe-mode rule contract to Ratis containers. It verifies that Ratis replication uses the generic container safe-mode behavior with `RatisReplicationConfig(THREE)`.

## Important APIs, Types, and Functions
- Constructs `RatisContainerSafeModeRule`.
- Provides `ReplicationType.RATIS`.
- Mocks `ContainerInfo` with `RatisReplicationConfig.getInstance(THREE)`, nonzero keys, lifecycle state, and IDs.

## Control Flow
All test behavior is inherited from `AbstractContainerSafeModeRuleTest`. This subclass supplies Ratis-specific rule creation and mock container metadata.

## State and Persistence Behavior
State is in-memory through mocks and inherited rule internals. No DB is used.

## Dependencies and Integration Points
The subclass connects the Ratis rule to `ContainerManager`, `EventQueue`, `SCMSafeModeManager`, and safe-mode metrics in the inherited fixture.

## Risks and Edge Cases
The inherited suite covers lifecycle filtering, refresh, duplicate reports, min-replica processing, and validation mode. The Ratis-specific risk is ensuring the min-replica and config assumptions match factor THREE.

## Test Signals
The file guarantees the abstract safe-mode container contract is continuously exercised for the primary Ratis replication path.
