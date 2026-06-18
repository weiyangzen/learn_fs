<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelineClose.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelineClose.java

Purpose: Tests SCM and datanode behavior around closing pipelines with closed or open containers, pipeline close actions, Ratis log failure triggers, and duplicate close-trigger suppression.

Important APIs and types: Uses `MiniOzoneCluster`, `StorageContainerManager`, `ContainerManager`, `PipelineManager`, `PipelineActionHandler`, `SCMEvents.PIPELINE_ACTIONS`, `PipelineActionsFromDatanode`, `OzoneContainer`, `XceiverServerRatis`, `ClosePipelineCommandHandler`, `RaftGroupId`, and `ClosePipelineInfo`.

Control flow: Setup creates a three-node cluster and allocates a Ratis three container before each test. Tests close containers then close/delete pipelines, close a pipeline with an open container and wait for the container to enter `CLOSING`, inject a datanode pipeline action and wait for the datanode report to omit the pipeline, mock the event handler while triggering `handleNodeLogFailure`, and use reflection to pre-populate `pipelinesInProgress` before repeatedly calling `triggerPipelineClose`.

State and persistence behavior: SCM pipeline and container lifecycle state are mutated. Node-to-pipeline maps are updated on deletion. Datanode Ratis state and command handler in-progress sets affect whether duplicate close commands are emitted. No SCM restart is included.

Dependencies and integration points: Covers SCM event queue, datanode heartbeat pipeline actions, Ratis log failure handling, command dispatcher close-pipeline state, and container/pipeline manager interaction.

Risks: Reflection into `pipelinesInProgress` is implementation-sensitive. Log-based duplicate assertion depends on exact lowercase text. Event queue handler mocking adds another handler to a live queue and assumes captured action ordering. The init method changes some config after cluster build, so only config read later will see those values.

Test signals: Signals include pipeline container set size one then zero after container close, node pipeline mappings removed after delete, open container reaching `CLOSING` on pipeline close, datanode pipeline report no longer containing the closed ID, SCM `PipelineNotFoundException` after datanode action, captured CLOSE action for the right pipeline after log failure, and ten duplicate triggers producing ten skipped-close log messages.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelineClose.java -->
