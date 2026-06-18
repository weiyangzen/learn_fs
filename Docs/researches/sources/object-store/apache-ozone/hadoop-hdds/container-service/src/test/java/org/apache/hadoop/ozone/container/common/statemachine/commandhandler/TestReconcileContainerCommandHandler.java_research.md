# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/statemachine/commandhandler/TestReconcileContainerCommandHandler.java

## Purpose
`TestReconcileContainerCommandHandler` verifies datanode handling of reconcile-container commands, including task submission, incremental container report emission, and metrics delegation through the replication supervisor.

## Important APIs, Types, And Functions
- `ReconcileContainerCommandHandler.handle`, `getInvocationCount`, `getQueuedCount`, `getTotalRunTime`, `getAverageRunTime`, and `getMetricsName` are tested.
- `ReconcileContainerCommand` identifies containers to reconcile.
- `ReplicationSupervisor.addTask` is mocked to immediately run `ReconcileContainerTask`.
- `IncrementalReportSender<Container>` captures generated container reports.
- `ContainerController`, `KeyValueHandler`, `ContainerChecksumTreeManager`, and `DNContainerOperationClient` support task execution.

## Control Flow
Initialization creates three key-value containers with block metadata and DB paths under temporary directories, adds them to a `ContainerSet`, wires a real `KeyValueHandler` into a `ContainerController`, and mocks the supervisor to execute tasks synchronously. The report test sends reconcile commands for known containers and one unknown container. It expects reports for all known containers and no report for the unknown ID. The metrics test sends known commands, stubs supervisor metrics for the handler's metric name, and asserts invocation, queued, total runtime, average runtime, and metric-name values.

## State And Persistence Behavior
The test creates temporary metadata/DB paths and block metadata, so it is closer to persistence-facing behavior than a pure mock. The reconciliation operation emits container reports with non-zero data checksum values. Actual remote reconciliation is mocked.

## Dependencies And Integration Points
The file integrates command handling with replication supervisor tasks, checksum/reconcile task infrastructure, key-value handler/report generation, container controller, incremental report sender, and metrics. Layout parameterization covers container layout variants.

## Risks And Edge Cases
Covered risks include missing ICR emission after reconcile, unknown containers producing bogus reports, metric-name drift, queued count not reflecting supervisor state, and incomplete checksum reporting. The test notes current checksum implementation is incomplete and uses a mocked/non-zero checksum.

## Test Signals
Signals are captured report map size/content, non-zero data checksum assertions, invocation counts, and supervisor-backed metric values.
