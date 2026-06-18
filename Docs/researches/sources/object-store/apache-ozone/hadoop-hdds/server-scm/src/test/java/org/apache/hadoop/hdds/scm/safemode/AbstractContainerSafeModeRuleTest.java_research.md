# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/safemode/AbstractContainerSafeModeRuleTest.java

## Purpose
`AbstractContainerSafeModeRuleTest` is a shared test suite for container safe-mode rules. Subclasses provide RATIS or EC-specific rule construction and mocked containers, while this base verifies refresh behavior, container filtering, report processing, duplicate handling, metrics, and validation modes.

## Important APIs, Types, and Functions
- Abstract hooks `getReplicationType`, `createRule`, and `mockContainer` make the suite reusable for `RatisContainerSafeModeRule` and `ECContainerSafeModeRule`.
- `AbstractContainerSafeModeRule.refresh`, `validate`, `process`, `getCurrentContainerThreshold`, `getTotalNumberOfContainers`, `getMinReplica`, and `setValidateBasedOnReportProcessing` are under test.
- Mocks include `ContainerManager`, `ConfigurationSource`, `EventQueue`, `SCMSafeModeManager`, and `SafeModeMetrics`.

## Control Flow
Setup mocks container listings by replication type and deleted state, and configures `getContainer` lookups by ID. Tests create containers in various lifecycle states, construct a rule, call `refresh` or `process` with synthetic node registration reports, and assert thresholds or validation results. Metrics tests capture refresh durations and refresh counts.

## State and Persistence Behavior
The rule's state is in-memory: tracked containers, reported datanodes/replicas, validation mode, and computed threshold. Container manager state is represented by mutable lists. No DB persistence is involved.

## Dependencies and Integration Points
The suite integrates safe-mode rules with `ContainerManager` lifecycle filtering, `SCMDatanodeProtocolServer.NodeRegistrationContainerReport`, datanode IDs, and `SafeModeMetrics`.

## Risks and Edge Cases
Covered risks include deleted container removal on refresh, closed/quasi-closed handling, all-open/all-closed edge cases, duplicate reports from the same report object, skipped refresh when already valid, and validating from report processing rather than manager state. It also verifies min-replica-dependent processing by sending the required number of distinct reports.

## Test Signals
This base class is a high-value cross-rule contract: any subclass failing lifecycle filtering, duplicate suppression, metrics, or validation mode semantics will fail the inherited tests.
