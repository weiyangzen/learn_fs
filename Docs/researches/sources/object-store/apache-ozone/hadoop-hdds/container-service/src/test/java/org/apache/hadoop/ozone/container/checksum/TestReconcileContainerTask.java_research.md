## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/checksum/TestReconcileContainerTask.java

Purpose: this test class validates task status and equality behavior for `ReconcileContainerTask`.

Important APIs and tests: tests construct tasks from mocked `ContainerController`, mocked `DNContainerOperationClient`, and `ReconcileContainerCommand`. They inspect `AbstractReplicationTask.Status` transitions and Java equality.

Control flow and state: `testFailedTaskStatus` makes `mockController.reconcileContainer` throw `IOException`, then asserts the task moves from `QUEUED` to `FAILED`. `testSuccessfulTaskStatus` runs without exception and asserts `DONE`. Equality tests show tasks with the same container ID are equal even when peer sets differ, while different container IDs are not equal.

Persistence and integration: no filesystem or network persistence. The task integrates reconciliation command state, container controller repair logic, and replication task scheduling semantics.

Risks and test signals: equality ignoring peers means the scheduler deduplicates reconciliation per container ID, not per peer set. That prevents duplicate work but may hide peer-set changes if a queued task already exists. Status tests confirm exceptions are contained and reflected in task state.
