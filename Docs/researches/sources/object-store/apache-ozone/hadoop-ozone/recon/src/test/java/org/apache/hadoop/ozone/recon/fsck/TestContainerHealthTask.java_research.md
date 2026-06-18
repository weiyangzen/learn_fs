# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/fsck/TestContainerHealthTask.java

Purpose: This unit test verifies `ContainerHealthTask` execution wiring. It ensures the task obtains `ReconReplicationManager` from `ReconStorageContainerManagerFacade` and calls `processAll`, and that a failure from `processAll` is propagated rather than swallowed.

Important APIs/types/functions: It uses `ContainerHealthTask.runTask`, `ReconStorageContainerManagerFacade.getReplicationManager`, `ReconReplicationManager.processAll`, `ReconTaskConfig.setMissingContainerTaskInterval`, `ReconTaskStatusUpdaterManager.getTaskStatusUpdater`, and a mocked `ReconTaskStatusUpdater`.

Control flow: Each test mocks the Recon SCM facade and replication manager, returns the manager from `getReplicationManager`, constructs `ContainerHealthTask` with a two-second task interval and mocked task status updater manager, then calls `runTask`. The failure test stubs `processAll` to throw a `RuntimeException` and asserts the same message is seen by the caller.

State and persistence behavior: There is no persistence. Runtime state is mocked task configuration, updater lookup, and the replication manager invocation.

Dependencies and integration points: This is a scheduling/wiring guard for Recon's container health background task. It connects the task framework to the local Recon replication manager and task status updater infrastructure.

Risks: The test does not inspect task status updater side effects such as run timestamps or failure state, only the call to `processAll`. It also does not start a scheduler loop; `runTask` is invoked directly.

Test signals: `processAll` is invoked exactly once on success; when `processAll` throws `RuntimeException("processAll failed")`, `runTask` throws and preserves the message.
