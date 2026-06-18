# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMStateMachine.java

Purpose: Ratis state machine that applies committed SCM HA operations to `StorageContainerManager`, maintains last-applied transaction metadata, handles leadership callbacks, and installs checkpoints from leaders.

Important APIs and types: Extends `BaseStateMachine`; key methods are `registerInvoker`, `applyTransaction`, `notifyInstallSnapshotFromLeader`, `notifyLeaderChanged`, `notifyLeaderReady`, `notifyTermIndexUpdated`, `takeSnapshot`, `pause`, `reinitialize`, and `close`.

Control flow: `applyTransaction` begins transaction-buffer application, decodes `SCMRatisRequest`, invokes the registered `ScmInvoker`, treats nonfatal `SCMException` as client failure, refreshes safe mode when ready, updates transaction info and last-applied index, and terminates on fatal exceptions. Snapshot install asynchronously downloads and verifies a leader checkpoint, stores checkpoint/secret keys, and later `reinitialize` installs it, reinitializes the transaction buffer, sets the last-applied index, restores secret keys, and transitions lifecycle back to running.

State and persistence behavior: Stores invokers, transaction buffer, latest installing checkpoint/secret keys, current leader term, readiness flag, and Ratis storage. Snapshots flush the transaction buffer and persist transaction info.

Dependencies and integration points: Integrates Ratis callbacks with SCM safe mode, service manager, finalization manager, deleted block log, decommission manager, sequence ID generator, metrics, and HA manager checkpoint APIs.

Risks and test signals: Fatal exception handling can terminate SCM. Snapshot install depends on peer address matching and single pending checkpoint state. Tests should cover local apply dispatch, nonfatal/fatal exception behavior, safe-mode refresh, leader step-down/leader-ready notifications, transaction-info updates, snapshot flush semantics, secret-key reinitialize, and close behavior from SCM versus Ratis.
