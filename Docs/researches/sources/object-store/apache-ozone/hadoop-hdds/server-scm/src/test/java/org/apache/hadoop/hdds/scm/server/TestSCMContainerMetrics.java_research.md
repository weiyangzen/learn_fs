# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/server/TestSCMContainerMetrics.java

## Purpose
`TestSCMContainerMetrics` verifies that `SCMContainerMetrics` exports Hadoop metrics gauges for container lifecycle states and total container count.

## Important APIs, Types, and Functions
- `SCMContainerMetrics.getMetrics` is under test.
- `SCMMXBean.getContainerStateCount` supplies lifecycle-state counts.
- `MetricsCollector`, `MetricsRecordBuilder`, `MetricsInfo`, and `Interns.info` are mocked/verified.

## Control Flow
The test stubs a state-count map for OPEN, CLOSING, QUASI_CLOSED, CLOSED, DELETING, DELETED, and RECOVERING. It calls `getMetrics` and verifies `addGauge` calls for each exported metric except RECOVERING, plus `TotalContainers`.

## State and Persistence Behavior
There is no persistence. Metrics are generated from an in-memory map returned by the MXBean.

## Dependencies and Integration Points
The class integrates the SCM MXBean with Hadoop Metrics2 collection. Metric names and descriptions are part of the observable contract.

## Risks and Edge Cases
The test confirms total count includes all states in the map, including RECOVERING, even though no explicit recovering gauge is verified. It would catch metric renames, missing gauges, or total miscalculation.

## Test Signals
Exact `verify(...).addGauge(...)` assertions lock down emitted metric names, descriptions, and values.
