# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/container/balancer/TestContainerBalancerStatusInfo.java

## Purpose
`TestContainerBalancerStatusInfo` verifies the live and historical iteration statistics exposed by `ContainerBalancerTask.getCurrentIterationsStatistic`. It covers completed iterations, repeated reads, reads between iterations, delayed start, in-progress balancing, and a regression where sleeping balancing threads could trigger a null pointer exception.

## Important APIs, Types, and Functions
The suite uses `MockedSCM`, `TestableCluster`, `ContainerBalancerConfiguration`, `ContainerBalancerTask`, `ContainerBalancerTaskIterationStatusInfo`, `ContainerBalancer`, and `StorageContainerManager`. Assertion helpers include `verifyCompletedIteration`, `verifyStartedEmptyIteration`, `assertCurrentIterationStatisticWhileBalancingInProgress`, and `getTotalMovedData`.

## Control Flow and State Behavior
Synchronous tests run `mockedScm.startBalancerTask(config)` with two iterations and zero balancing interval, then assert two completed statistics entries. Re-requesting statistics after a delay must return equal entries, proving history is stable after completion. Asynchronous tests start tasks with long balancing intervals or delay flags and use `LambdaTestUtils.await` or sleeps to inspect partial progress.

Completed iteration validation checks iteration number, result string `ITERATION_COMPLETED`, non-null duration, positive scheduled/completed moves, zero failed/timeouts, positive scheduled and moved data, non-empty entering/leaving maps, and equality between total entering and leaving bytes. Delayed-start validation expects an initial iteration entry with no result and zero movement. In-progress validation intentionally avoids flaky counters and checks only that iteration 2 has no result yet, no failed/timeouts, and positive entering/leaving node sizes.

The regression test for HDDS-11350 enables DU triggering so the balancing thread sleeps while waiting for datanode usage updates, starts the task on a daemon thread, and asserts `getCurrentIterationsStatistic` does not throw.

## Dependencies and Integration Points
This suite depends on `MockedSCM` for asynchronous balancer execution, Ozone configuration keys for safe-mode wait behavior, `ArithmeticUtils.addAndCheck` for summing movement maps, and `LambdaTestUtils` for wait loops.

## Risks and Test Signals
Risks include unstable status snapshots, missing current-iteration records during sleep/delay windows, incorrect entering/leaving accounting, null dereferences, and mutation of completed history. Signals are status list sizes, iteration fields, movement counters, map contents, and exception-free statistic retrieval.
