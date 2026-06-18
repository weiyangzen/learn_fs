# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestDataNodeSafeModeRule.java

## Purpose
`TestDataNodeSafeModeRule` validates the datanode-count safe-mode rule. It checks both report-processing validation and direct `NodeManager` validation against the configured minimum datanode count.

## Important APIs, Types, and Functions
- `DataNodeSafeModeRule.validate`, `setValidateBasedOnReportProcessing`, and event handling for `SCMEvents.NODE_REGISTRATION_CONT_REPORT` are central.
- Config key `HDDS_SCM_SAFEMODE_MIN_DATANODE` sets the threshold.
- `SafeModeMetrics.getCurrentRegisteredDatanodesCount` is verified.

## Control Flow
`setup` creates an `OzoneConfiguration`, real `EventQueue`, mocked `NodeManager`, mocked safe-mode manager, and real metrics. Tests fire node registration reports through the event queue and wait for log output showing registered/required counts. The NodeManager mode test disables report-processing validation and stubs healthy-node lists before calling `validate`.

## State and Persistence Behavior
State is in-memory: a set/count of registered datanodes and metrics gauges. No persistent SCM state is used.

## Dependencies and Integration Points
The rule integrates with SCM event dispatch, datanode registration reports, `NodeManager.getNodes(NodeStatus.inServiceHealthy())`, and safe-mode metrics.

## Risks and Edge Cases
The tests cover zero initial nodes, partial registration below threshold, crossing the threshold, and validation from manager state rather than event history. Duplicate datanode reports are not explicitly tested here.

## Test Signals
The log wait plus metrics count assertion ensures both user-visible status and metrics are updated as registrations arrive.
