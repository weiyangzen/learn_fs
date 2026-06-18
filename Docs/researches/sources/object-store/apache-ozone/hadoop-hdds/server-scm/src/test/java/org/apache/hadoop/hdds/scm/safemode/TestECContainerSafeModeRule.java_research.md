# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestECContainerSafeModeRule.java

## Purpose
`TestECContainerSafeModeRule` applies the shared `AbstractContainerSafeModeRuleTest` contract to EC containers. It ensures EC-specific minimum replica logic and lifecycle filtering satisfy the same safe-mode expectations.

## Important APIs, Types, and Functions
- Constructs `ECContainerSafeModeRule`.
- Provides `ReplicationType.EC`.
- Mocks `ContainerInfo` with `ECReplicationConfig(3, 2)`, nonzero keys, lifecycle state, and container IDs.

## Control Flow
All concrete test execution is inherited from the abstract base. This subclass only supplies EC rule construction and EC-flavored mocked container metadata.

## State and Persistence Behavior
No persistent state is used. Mocked containers expose EC replication config and lifecycle state to the inherited tests.

## Dependencies and Integration Points
The subclass connects `ECContainerSafeModeRule` to `ContainerManager`, `EventQueue`, and `SCMSafeModeManager` through the inherited fixture.

## Risks and Edge Cases
The inherited tests cover refresh, duplicate reports, state filtering, and report-processing validation. EC-specific variation is the minimum replica value derived from data/parity config.

## Test Signals
This file is a compact but important signal that the generic safe-mode container rule contract is valid for EC replication, not only RATIS.
