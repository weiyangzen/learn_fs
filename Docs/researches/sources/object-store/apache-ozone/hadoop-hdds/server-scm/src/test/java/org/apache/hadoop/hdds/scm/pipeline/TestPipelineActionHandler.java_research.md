# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelineActionHandler.java

Purpose: tests `PipelineActionHandler`, especially close-pipeline actions reported by datanodes and leader/follower behavior.

Important APIs and types: uses `PipelineActionHandler`, `PipelineActionsFromDatanode`, `PipelineActionsProto`, `PipelineAction`, `ClosePipelineInfo`, `PipelineManager`, `SCMContext`, `EventQueue`, `SCMEvents.DATANODE_COMMAND`, and `CommandForDatanode`.

Control flow: helper constructs a datanode action containing one CLOSE action with reason `PIPELINE_FAILED`. Valid-pipeline leader test expects `PipelineManager.closePipeline`. Follower test updates context to non-leader and expects no close and no command event. Unknown-pipeline leader test makes `closePipeline` throw `PipelineNotFoundException` and expects a datanode command event, while the follower variant expects no event.

State and persistence behavior: no persistent state; behavior depends on `SCMContext` leadership and mocked pipeline manager exceptions.

Dependencies and integration points: covers datanode heartbeat action handling, pipeline manager close API, SCM command event emission, and HA leader gating.

Risks and edge cases: only CLOSE action is covered. The tests verify interactions, not command payload details.

Test signals: good signal that only leaders act on pipeline actions and that unknown pipelines cause corrective datanode commands only from leaders.
