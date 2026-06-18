## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/ReconStaleNodeHandler.java

Purpose: `ReconStaleNodeHandler` extends SCM stale-node handling with an immediate pipeline metadata refresh in Recon.

Important APIs and types: extends `StaleNodeHandler`, stores `PipelineSyncTask`, and overrides `onMessage(DatanodeDetails, EventPublisher)`.

Control flow: the handler delegates to the parent stale-node logic, then calls `pipelineSyncTask.initializeAndRunTask`. Exceptions from the task are logged and swallowed.

State and persistence: no local state beyond the task reference. Parent logic updates node/pipeline runtime state; the pipeline sync task persists or updates pipeline metadata through its own manager.

Dependencies and integration points: registered by the facade for `SCMEvents.STALE_NODE`. It couples node liveness transitions to pipeline reconciliation because stale datanodes can affect pipeline health and membership.

Risks and edge cases: every stale-node event can trigger a full pipeline sync task, which may be expensive under churn. If the task fails, Recon logs but does not retry within this handler.

Test signals: no direct test was found. Useful tests should verify parent invocation order and that pipeline sync is triggered once per stale event with failure logging.
