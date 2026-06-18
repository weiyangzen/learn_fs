# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/NodeAddressUpdateHandler.java

Purpose: `NodeAddressUpdateHandler` handles datanode IP or hostname changes. It closes stale pipelines, notifies SCM service observers, and asks the decommission manager to continue any admin workflow for the updated datanode.

Important APIs and types: It implements `EventHandler<DatanodeDetails>` and depends on `PipelineManager`, `NodeDecommissionManager`, `SCMServiceManager`, and `SCMService.Event.NODE_ADDRESS_UPDATE_HANDLER_TRIGGERED`.

Control flow: `onMessage` logs the address update context, calls `pipelineManager.closeStalePipelines`, notifies the service manager, and calls `decommissionManager.continueAdminForNode` unconditionally. `NodeNotFoundException` is logged as an error.

State and persistence behavior: It can mutate pipeline state and in-memory admin-monitor tracking. It does not persist address information itself; the updated datanode details are already in node-manager state before this handler runs.

Dependencies and integration points: It connects node registration/update handling with pipeline cleanup and decommission/maintenance workflow recovery. It is useful when the same datanode identity appears with updated network coordinates.

Risks: Unlike `NewNodeHandler`, it calls `continueAdminForNode` even if the node is currently `IN_SERVICE`; the manager checks state and only monitors admin states. Errors from stale pipeline close outside `NodeNotFoundException` would abort service notification and admin continuation.

Test signals: Tests should cover stale pipeline close calls, service notification, continuation call, and `NodeNotFoundException` logging.
