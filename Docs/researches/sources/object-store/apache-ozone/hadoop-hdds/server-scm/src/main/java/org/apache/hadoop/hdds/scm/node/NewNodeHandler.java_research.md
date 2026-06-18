# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/NewNodeHandler.java

Purpose: `NewNodeHandler` handles newly registered datanode events by closing stale pipelines, notifying SCM services, and resuming decommission or maintenance workflows if the datanode reports a persisted non-`IN_SERVICE` operational state.

Important APIs and types: It implements `EventHandler<DatanodeDetails>` and uses `PipelineManager.closeStalePipelines`, `NodeDecommissionManager.continueAdminForNode`, `SCMServiceManager.notifyEventTriggered`, and `SCMService.Event.NEW_NODE_HANDLER_TRIGGERED`.

Control flow: On event, it closes stale pipelines for the datanode, notifies service listeners, then checks `datanodeDetails.getPersistedOpState`. If the persisted state is not `IN_SERVICE`, it asks the decommission manager to continue the admin workflow. `NodeNotFoundException` is logged as unexpected.

State and persistence behavior: It mutates pipeline state through the pipeline manager and may re-enqueue the datanode into the in-memory admin monitor. It relies on persisted operational state reported by the datanode at registration.

Dependencies and integration points: It connects registration, pipeline recovery, HA/service readiness notifications, and admin workflow recovery after SCM restart or datanode re-registration.

Risks: Continuing admin workflow is leader-gated inside the decommission manager, so followers ignore it. If pipeline close fails through unchecked exceptions, later workflow recovery will not run. The handler assumes the node was just registered, so `NodeNotFoundException` is only logged.

Test signals: Tests should verify stale pipeline close, service event notification, conditional `continueAdminForNode`, leader/follower behavior through manager tests, and exception logging.
