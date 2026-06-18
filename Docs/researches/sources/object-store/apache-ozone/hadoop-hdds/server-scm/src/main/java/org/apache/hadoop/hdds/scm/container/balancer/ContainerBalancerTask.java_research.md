<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancerTask.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancerTask.java

## Purpose
Runs the container balancer loop. It classifies datanodes by utilization, selects source/target/container moves, schedules asynchronous moves, tracks per-iteration statistics and metrics, persists next-iteration progress, and stops when the cluster is balanced, configuration is exhausted, or SCM state becomes invalid.

## Important APIs, Types, And Functions
`ContainerBalancerTask` implements `Runnable`. Key methods are `run`, `stop`, `balance`, `initializeIteration`, `doIteration`, `matchSourceWithTarget`, `processMoveSelection`, `moveContainer`, `checkIterationMoveResults`, `cancelMovesThatExceedTimeoutDuration`, `updateTargetsAndSelectionCriteria`, `incSizeSelectedForMoving`, `resetState`, `calculateAvgUtilization`, and `getCurrentIterationsStatistic`. It uses `FindSourceGreedy`, `FindTargetGreedyByUsageInfo` or `FindTargetGreedyByNetworkTopology`, `ContainerBalancerSelectionCriteria`, `MoveManager`, and `ContainerBalancerMetrics`. Enums `IterationResult` and `Status` represent loop and task state.

## Control Flow
`run` optionally sleeps after safe-mode exit, calls `balance`, and marks STOPPED in `finally`. `balance` loops from persisted `nextIterationIndex` through configured iterations, resets state, optionally triggers datanode DU refresh and waits for node reports, initializes over/under-utilized sets, executes an iteration, records status info, clears strategy traffic maps, increments iteration metrics, persists next iteration on success, sleeps between iterations, and stops with persisted `shouldRun=false` when complete or no longer balanceable. `doIteration` repeatedly checks move-size and datanode-involvement limits, adapts candidate sets near limits, gets a source, finds a target/container, and schedules the move. Move futures update metrics and actual bytes moved; iteration end waits for all futures or cancels timed-out moves.

## State And Persistence
Runtime state includes utilization lists, selected source/target sets, container source/target maps, scheduled and actual byte counts, move futures, current iteration start time, status queue, and strategy traffic maps. Persistent state is only through `ContainerBalancer.saveConfiguration`, which stores `shouldRun` and next iteration index. Actual container movement state is owned by `MoveManager`, replication manager, datanodes, and container reports.

## Dependencies And Integration Points
Depends on `StorageContainerManager`, `NodeManager`, `ContainerManager`, `ReplicationManager`, `MoveManager`, placement validation, network topology, SCM leader/safe-mode context, Ozone and HDDS timing config, balancer config, datanode usage info, and status DTO classes. It is the main orchestration point connecting SCM utilization observations to replication-manager move operations.

## Risks And Test Signals
`sizeActuallyMovedInLatestIteration` is updated from async callbacks without synchronization. Moves are treated optimistically for scheduling when futures are still running, so later failures can leave selection accounting more conservative than actual movement. Datanode-involvement adaptation depends on integer truncation of ratio times cluster size. `withinThresholdUtilizedNodes` is populated but not used as candidates. Tests should cover average utilization, include/exclude node filtering, safe-mode/leader invalidation, DU-trigger wait interruption, over/under threshold classification, candidate adaptation at limits, duplicate container prevention, move-result metric classification, timeout cancellation, persisted next iteration, stop behavior, and current-iteration status generation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancerTask.java -->
