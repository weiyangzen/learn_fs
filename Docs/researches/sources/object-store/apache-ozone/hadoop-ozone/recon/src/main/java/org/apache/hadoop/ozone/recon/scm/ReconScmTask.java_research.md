## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconScmTask.java

Purpose: `ReconScmTask` is the abstract base for Recon background tasks that maintain SCM-derived metadata, such as pipeline sync, container health, and container size counts.

Important APIs and types: constructor obtains a `ReconTaskStatusUpdater` by task name. `start`, `stop`, `isRunning`, `canRun`, `getTaskName`, `getTaskStatusUpdater`, `initializeAndRunTask`, `run`, and `runTask` define the lifecycle.

Control flow: `start` creates a daemon thread named by the task class and runs the subclass `run` loop. `stop` clears `running` and notifies waiters. `initializeAndRunTask` records run start/completion around a single `runTask` invocation, used by event handlers for immediate recomputation.

State and persistence: runtime state is `taskThread` and volatile `running`. Persistent task status is delegated to `ReconTaskStatusUpdater`, which records timing/status in Recon task status storage.

Dependencies and integration points: extended by `PipelineSyncTask`, `ContainerHealthTask`, and `ContainerSizeCountTask`. `ReconStorageContainerManagerFacade` starts/stops tasks, while stale/dead handlers call `initializeAndRunTask` for immediate refresh.

Risks and edge cases: `isRunning` can return true for an alive thread even if `running` is false. `stop` does not interrupt the thread; subclasses must observe `canRun` and wait/notify correctly. `initializeAndRunTask` does not record failure completion if `runTask` throws unless callers handle it.

Test signals: task-specific tests cover subclasses such as `TestContainerHealthTask`. Base-class tests should cover lifecycle idempotency, daemon thread creation, and status updater calls around manual runs and exceptions.
