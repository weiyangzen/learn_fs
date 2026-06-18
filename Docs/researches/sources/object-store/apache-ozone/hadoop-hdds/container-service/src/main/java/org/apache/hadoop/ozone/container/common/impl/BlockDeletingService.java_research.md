<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/BlockDeletingService.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/BlockDeletingService.java

Purpose: background datanode service that selects closed or quasi-closed containers with pending deleted blocks and schedules `BlockDeletingTask` workers.

Important APIs and control flow: constructors configure `BackgroundService`, choose a `ContainerDeletionChoosingPolicy` from config, register dynamic reconfiguration callbacks, and create metrics. `getTasks` calls `chooseContainerForBlockDeletion`, builds one task per selected container, and records chosen block/container counts. `chooseContainerForBlockDeletion` streams over the `OzoneContainer` `ContainerSet`, filters containers with pending deletion, checks deletion eligibility, totals pending block counts and bytes, and delegates final selection to the policy. `isDeletionAllowed` rejects unsupported container types, non-closed states, invalid origin pipeline IDs, and Ratis containers whose close index is not replicated across all peers.

State and persistence: service state is scheduled executor configuration, metrics, and references to container set and checksum tree manager. It does not directly persist deletes; tasks do. Reconfiguration shuts down and restarts the service with new interval, timeout, and worker count.

Dependencies and integration: integrates with `OzoneContainer`, `XceiverServerRatis`, `PipelineID`, `DatanodeConfiguration`, deletion policies, `ContainerUtils`, `BlockDeletingTask`, and `ContainerChecksumTreeManager`.

Risks and test signals: tests should cover Ratis gating by min replicated index, invalid or absent pipeline IDs, EC containers with empty origin pipeline IDs, reconfiguration restart without deadlock, and metrics for pending bytes/counts. The policy only supports `KeyValueContainer`; new container types require both utility and task builder extensions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/impl/BlockDeletingService.java -->
