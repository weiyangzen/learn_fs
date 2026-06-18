# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/upgrade/FinalizationManagerImpl.java

Purpose: `FinalizationManagerImpl` composes the SCM upgrade finalizer, persistent finalization state manager, and finalization context. It is the concrete bridge between client requests, leader-resume behavior, HA replication, and layout-version upgrade execution.

Important APIs and types: It owns an `SCMUpgradeFinalizer`, `SCMUpgradeFinalizationContext`, `SCMStorageConfig`, `OzoneConfiguration`, `HDDSLayoutVersionManager`, `FinalizationStateManager`, and a named `ThreadFactory`. Its builder requires configuration, layout version manager, storage config, HA manager, finalization store, and finalization executor. It uses `FinalizationStateManagerImpl.Builder` to wrap the state manager with an HA/Ratis proxy.

Control flow: Construction initializes common fields and creates the state manager. `buildUpgradeContext` assembles the objects finalization actions need, installs it into the state manager, and builds a thread name prefix from `SCMContext`. `finalizeUpgrade` validates that context exists and delegates to `SCMUpgradeFinalizer.finalize`. `queryUpgradeFinalizationProgress` returns readonly status without mutating client tracking when requested, otherwise delegates to `reportStatus`. `onLeaderReady` starts a background single-thread executor, checks the current checkpoint, and resumes finalization if it has started but not completed.

State and persistence behavior: Persistent state is delegated to `FinalizationStateManager`; this class holds runtime references and the finalizer. On leader resume failure it terminates the process to avoid an SCM leader remaining in an inconsistent upgrade state. The single-thread executor is created on each leader-ready call and not explicitly shut down.

Dependencies and integration points: It integrates the generic Ozone upgrade finalization framework with SCM HA (`SCMHAManager`), the SCM metadata finalization table, Ratis transaction buffer, storage VERSION files, node/pipeline managers, and SCM context. Tests can inject a custom state manager through the protected constructor.

Risks: `onLeaderReady` can create a new executor per invocation; repeated calls are expected to be rare but could leak idle threads. Resume failure terminates SCM, which is deliberate but high impact. Builder null checks catch configuration mistakes late at construction. Querying with `readonly=true` bypasses takeover behavior and returns empty messages.

Test signals: Important assertions include builder required fields, context-build propagation, `finalizeUpgrade` precondition, readonly query behavior, checkpoint delegation, reinitialize delegation, leader-ready resume only for started/incomplete checkpoints, and termination path on resume failure.
