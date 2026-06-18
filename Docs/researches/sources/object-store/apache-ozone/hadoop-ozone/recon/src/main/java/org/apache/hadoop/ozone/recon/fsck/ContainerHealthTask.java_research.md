## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/fsck/ContainerHealthTask.java

Purpose: scheduled Recon SCM task that runs local container health analysis using Recon's `ReconReplicationManager`.

Important APIs/types/functions: `run()` loops with task lifecycle controls; `runTask()` casts SCM replication manager to `ReconReplicationManager` and invokes `processAll`; `stop()` unregisters metrics.

Control flow: each cycle records start time, calls `initializeAndRunTask`, sleeps for at least 60 seconds and otherwise `interval - elapsed`, exits on interruption, and logs other exceptions. `runTask` increments success/failure metrics and records runtime in a finally block.

State and persistence: durable DB writes are delegated to `ReconReplicationManager`. Task-local state includes interval and `ContainerHealthTaskMetrics`. Dependencies are `ReconScmTask`, `ReconStorageContainerManagerFacade`, `ReconTaskConfig`, and metrics.

Risks: hard cast assumes facade returns the Recon-specific replication manager. Repeated failures log but do not back off beyond normal loop sleep. Tests should cover success/failure metrics, sleep interval calculation, interruption, stop unregistering metrics, and integration with a mocked Recon replication manager.
