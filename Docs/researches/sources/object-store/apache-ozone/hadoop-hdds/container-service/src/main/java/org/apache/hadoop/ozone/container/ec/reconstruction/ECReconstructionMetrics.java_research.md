# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ec/reconstruction/ECReconstructionMetrics.java

## Purpose
`ECReconstructionMetrics` is the metrics source for datanode EC reconstruction coordination. It records container reconstruction attempts/failures and reconstructed block-group attempts/failures.

## Important APIs and Types
The class is annotated with Hadoop metrics annotations and registers under the source name `ECReconstructionMetrics` in the Ozone metrics context. `create()` registers a new instance with `DefaultMetricsSystem`; `unRegister()` unregisters it. Increment APIs are `incBlockGroupReconstructionTotal`, `incBlockGroupReconstructionFailsTotal`, `incReconstructionTotal`, and `incReconstructionFailsTotal`. Getter APIs expose reconstruction total and block-group reconstruction total.

## Control Flow
Metrics registration is explicit through `create`. The coordinator increments success counters after all target containers are closed and increments failure counters in the exception cleanup path. The counters are `MutableCounterLong` fields injected by the metrics system based on `@Metric`.

## State and Persistence
All state is in memory inside Hadoop metrics counters. The class does not persist data to disk. Metrics visibility is through the process metrics system and ends when unregistered or when the process exits.

## Dependencies and Integration Points
`ECReconstructionCoordinator` receives an instance and records reconstruction results. `DatanodeStateMachine` creates the coordinator and metrics, and tests use `ECReconstructionMetrics.create()` in reconstruction integration scenarios. The class depends on Hadoop metrics2, `DefaultMetricsSystem`, and `OzoneConsts.OZONE`.

## Risks and Test Signals
Registration uses a fixed source name, so repeated `create()` without `unRegister()` can conflict or leak metrics in long-running test JVMs. Failure counters do not have public getters, which makes direct assertion harder. Existing integration tests in `TestContainerCommandsEC` assert success totals and block-group counts; additional tests could cover failure counter increments and unregister/re-register behavior.
