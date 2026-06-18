## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/PipelineSyncTask.java

Purpose: background Recon SCM task that syncs pipeline state from SCM and reconciles operational state for dead nodes.

Important APIs/types/functions: constructor; `run`; `runTask`; private `syncOperationalStateOnDeadNodes`.

Control flow: `run` loops while task can run, calls `initializeAndRunTask`, sleeps configured interval, and records failure status on throwable. `runTask` takes a fair write lock, fetches pipelines from SCM, initializes Recon pipeline manager, syncs dead-node operational state, logs duration, and marks status success. Dead-node sync fetches Recon dead nodes, gets SCM nodes, filters matching datanodes, warns if SCM does not report DEAD, and updates Recon node operational state from SCM.

State and persistence: modifies in-memory Recon pipeline/node manager state and task status; persistence depends on those managers/updaters. Dependencies are `StorageContainerServiceProvider`, `ReconPipelineManager`, `ReconNodeManager`, `ReconTaskConfig`, and task status updater.

Risks: any throwable exits the loop rather than continuing after one failed iteration. Uses write lock though no read path appears in this class. Matching relies on `DatanodeDetails.equals`. Tests should cover pipeline initialization, dead-node operational updates, SCM state mismatch warning, exceptions from SCM/node manager, status updater success/failure, interruption, and lock release.
